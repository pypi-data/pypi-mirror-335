import snowflake.connector as sf
from .Logging import Debug  # Import from same package

class SnowflakeConnection:
    """Handles establishing and managing connections to Snowflake."""

    DEFAULTS = {
        "snowflake_username": "snowflake username",
        "snowflake_account": "snowflake account"
    }
    
    _connection = None  # Instance variable

    @staticmethod
    def establish_connection(user_name: str = DEFAULTS["snowflake_username"], account: str = DEFAULTS["snowflake_account"]) -> sf.connection:
        """Establishes a connection to Snowflake.

        Uses either a credentials file or manual login via username and account.

        Args:
            user_name (str, optional): The Snowflake username. Defaults to 'DEFAULTS["snowflake_username"]'.
            account (str, optional): The Snowflake account ID. Defaults to 'DEFAULTS["snowflake_account"]'.
            verbose (bool, optional): set True to enable DEBUG output. Defaults to False.

        Returns:
            sf.connection: A Snowflake account connection object.

        Raises:
            sf.errors.Error: If connection fails.
        """

        if SnowflakeConnection._connection:
            return SnowflakeConnection._connection

        try:
            if user_name == SnowflakeConnection.DEFAULTS["snowflake_username"] or account == SnowflakeConnection.DEFAULTS["snowflake_account"]:
                SnowflakeConnection._connection = sf.connect()
            else:
                SnowflakeConnection._connection = sf.connect(
                    user=user_name,
                    account=account,
                    authenticator="externalbrowser"
                )
            return SnowflakeConnection._connection
        
        except Exception as e:
            Debug.log(f"\nCould not connect to Snowflake, did you create a .toml file?\nRemember you can always connect using account + username.\nError message: {e}", 'ERROR')
            raise sf.errors.ConfigSourceError