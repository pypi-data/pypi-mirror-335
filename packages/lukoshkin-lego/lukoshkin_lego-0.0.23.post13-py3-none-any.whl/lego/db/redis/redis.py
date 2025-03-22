"""Context class for keeping track of the conversation state in Redis."""

from typing import Any

from redis import asyncio as redis

from lego.models import ReprEnum
from lego.settings import RedisConnection


class NotSet:
    """Sentinel type for not set values."""


_sentinel = NotSet()


class RedisContext:
    """Redis context with get, set, and delete methods."""

    def __init__(
        self,
        ctx_id: str,
        connection: RedisConnection,
        create_parents_on_set: bool = False,
        stricter_key_checking: int = 1,
    ) -> None:
        self._create_parents_on_set = create_parents_on_set
        self._stricter_key_checking = stricter_key_checking
        self.redis = redis.Redis(**connection.model_dump())  # type: ignore[attr-defined]
        self.redon = self.redis.json()
        self.ctx_id = ctx_id

    async def init(self) -> None:
        """Initialize the main state."""
        await self.redon.set(self.ctx_id, "$", {}, nx=True)

    async def ctx_ttl(self) -> float | None:
        """Get the time-to-live for the RedisContext."""
        return await self.redis.ttl(self.ctx_id)

    async def set_expiration_time(
        self,
        expires_in: float | None = None,
        init_if_need_be: bool = False,
    ) -> None:
        """
        Set the expiration time for the RedisContext.

        Args:
            :param expires_in: If provided, the expiration time in seconds.
                Will be rounded to the integer by discarding the decimal part.
        """
        if expires_in is not None:
            if expires_in < 0 and expires_in != -1:
                raise ValueError(
                    f"{expires_in=} must be either -1 or a positive number."
                )
        if await self.ctx_ttl() == -2:
            if not init_if_need_be:
                raise ValueError(
                    "Context is not initialized."
                    " Either because expired, deleted, or never initialized."
                )
            await self.init()

        if expires_in is not None and expires_in > 0:
            await self.redis.expire(self.ctx_id, int(expires_in))

    async def get(  # type: ignore[misc]
        self,
        key: str | ReprEnum | None = None,
        fallback_value: Any = None,
        prefix: str | None = None,
        throw_error_if_missing: bool = False,
    ) -> Any:
        """
        Get a key-value pair from the conversation state.

        Args:
            :param key: The key to get the value.
            :param fallback_value: The value to return if the key is not found.
            :param throw_error_if_missing: If True, raise an error
            if the key is not found.
        """
        uri = self._prefix_key(key, prefix)
        result = await self.redon.get(self.ctx_id, uri)
        if throw_error_if_missing and not result:
            raise KeyError(
                f"Missing parent in the {key}"
                f" of the RedisContext: {self.ctx_id}"
            )
        return result[0] if result else fallback_value

    async def verify_key_path(
        self,
        key_path: str,
        create_parents: bool = False,
    ) -> None:
        """
        Check if the key is valid or create a new path.

        Args:
            :param key_path: The key path to check or create.
            :param create_parents: If True, create the parent keys
            if the corresponding dicts do not exist.
        """

        async def check_create_key(uri: str) -> None:
            try:
                value = await self.get(uri, throw_error_if_missing=True)
                if not isinstance(value, dict):
                    raise ValueError(f"Key {uri} is not a dictionary.")
            except KeyError as exc:
                if not create_parents:
                    raise exc

                await self.redon.set(self.ctx_id, uri, {})

        uri = "$"
        for key in str(key_path).split("."):
            if key == "$":
                continue

            if self._stricter_key_checking > 0:
                msg = (
                    (
                        "Key must be a valid identifier."
                        " It must start with a letter or an underscore, and"
                        " can only contain letters, digits, and underscores."
                    )
                    if self._stricter_key_checking == 1
                    else (
                        "Key must have identifier+ format ('+' means dashes"
                        " are allowed as well as the key string can start"
                        " with a digit)"
                    )
                )
                msg += f"\nProvided key: {key}"
                checked_key = (
                    key
                    if self._stricter_key_checking > 1
                    else f"a{key.replace("-", "_")}"
                )
                if not checked_key.isidentifier():
                    raise ValueError(msg)
            await check_create_key(uri)
            uri += f".{key}"

    async def set_(
        self,
        key: str | ReprEnum,
        value: Any,  # type: ignore[misc]
        prefix: str | None = None,
        list_append: bool = False,
        create_parents: bool | None = None,
    ) -> None:
        """
        Set a key-value pair in the conversation state.

        Args:
            :param key: The key to set the value.
            :param value: The value to set.
            :param list_append: If True, the value will be appended to the list
            :param prefix: The prefix to the key.
            :param create_parents: If True, create the parent keys
        """
        if create_parents is None:
            create_parents = self._create_parents_on_set

        uri = self._prefix_key(key, prefix)
        await self.verify_key_path(uri, create_parents=create_parents)

        if list_append:
            potential_list = await self.get(key)
            if potential_list is None:
                await self.redon.set(self.ctx_id, uri, [])
            elif not isinstance(potential_list, list):
                raise ValueError(f"Not a list under the key {key}.")
            await self.redon.arrappend(self.ctx_id, uri, value)
            return

        await self.redon.set(self.ctx_id, uri, value)

    async def count(
        self, key: str | ReprEnum, prefix: str | None = None
    ) -> int:
        """Update the counter under the `key`."""
        if counter := await self.get(key, prefix=prefix):
            if not isinstance(counter, int):
                raise TypeError("Counter is not an integer.")
        else:
            await self.set_(key, 0, prefix=prefix)

        uri = self._prefix_key(key, prefix)
        res = await self.redon.numincrby(self.ctx_id, uri, 1)
        return res[0]

    async def delete(
        self,
        key: str | ReprEnum | None = None,
        prefix: str | None = None,
        throw_error_if_missing: bool = True,
    ) -> Any | None:
        """
        Delete a key-value pair from the conversation state.

        If the key is not found, it will do nothing.
        """
        uri = self._prefix_key(key, prefix)
        value = await self.get(
            uri,
            throw_error_if_missing=throw_error_if_missing,
            fallback_value=_sentinel,
        )
        if value is _sentinel:
            return None

        await self.redon.delete(self.ctx_id, uri)
        return value

    async def close(self) -> None:
        """Close the Redis connection."""
        await self.redis.aclose()

    def _prefix_key(
        self, key: str | ReprEnum | None, prefix: str | None = None
    ) -> str:
        if not prefix and key == "$":
            return "$"

        if prefix and prefix.endswith("."):
            raise ValueError("Malformed prefix: it cannot end with a dot.")

        if not key:
            return prefix or "$"

        key = str(key)
        if not key.isascii():
            raise ValueError(f"Key must be ASCII: {key}")

        if (
            key.startswith(".")
            or key.endswith(".")
            or ".." in key
            or "$.$" in key
        ):
            raise ValueError(
                f"Malformed key: {key}\n"
                "Disallowed patterns in the current implementation: "
                " 'key.' or '.key' or 'double..dot' or '$.$'"
            )
        if key.startswith("$"):
            if prefix or key[1] != ".":
                raise ValueError("Key cannot start with $")

        uri = f"{prefix or '$'}.{key.lstrip('$.')}"
        if not uri.startswith("$"):
            uri = f"$.{uri}"
        return uri
