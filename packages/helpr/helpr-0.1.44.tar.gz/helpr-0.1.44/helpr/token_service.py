"""
JWT Token Helper module for generating and verifying toke.
"""
from typing import Any, Dict
from datetime import datetime, timedelta
from authlib.jose import JsonWebToken
from authlib.jose.errors import ExpiredTokenError, DecodeError, InvalidTokenError
from .exceptions import AppException

class TokenException(AppException):
    """Base exception for token-related error"""
    def __init__(self, message: str, error_code: int = 1000, http_code: int = 400):
        super().__init__(message=message, error_code=error_code, http_code=http_code)

class TokenTypeMismatchException(TokenException):
    """Raised when token type doesn't match expected type"""
    def __init__(self, message: str = "Token type does not match expected type"):
        super().__init__(message=message, error_code=1001, http_code=400)

class TokenGenerationException(TokenException):
    """Raised when token generation fails"""
    def __init__(self, message: str = "Failed to generate token"):
        super().__init__(message=message, error_code=1002, http_code=500)

class TokenVerificationException(TokenException):
    """Raised when token verification fails"""
    def __init__(self, message: str = "Failed to verify token"):
        super().__init__(message=message, error_code=1003, http_code=401)

class JWTHelper:
    """Helper class for JWT token operations"""
    
    def __init__(self, key_provider, algorithm: str = 'RS256'):
        """
        Initialize the JWT Helper.
        
        Args:
            key_provider: Provider object that supplies private and public keys
            algorithm (str): Algorithm to use for token signing
        """
        self.key_provider = key_provider
        self._algo = algorithm
        
    def generate_token(
        self,
        sub: Any,
        expiration_minutes: int,
        token_type: str,
        custom_payload: Dict[str, Any] = None
    ) -> str:
        """
        Generate a JWT token.

        Args:
            sub: Token subject
            expiration_minutes (int): Minutes until expiration
            token_type (str): Token type (e.g., "access" or "refresh")
            custom_payload (dict, optional): Additional claims to include

        Returns:
            str: Generated JWT token

        Raises:
            TokenGenerationException: If token generation fails
        """
        try:
            expiration_time = datetime.utcnow() + timedelta(minutes=expiration_minutes)
            exp_claim = int(expiration_time.timestamp())
            
            payload = {
                'sub': sub,
                'exp': exp_claim,
                'token_use': token_type
            }
            
            if custom_payload:
                payload.update(custom_payload)
                
            jwt_instance = JsonWebToken(algorithms=self._algo)
            token = jwt_instance.encode(
                header={
                    'alg': self._algo,
                    'typ': 'JWT',
                    'kid': self.key_provider.public_key_kid()
                },
                payload=payload,
                key=self.key_provider.private_key()
            )
            
            return token.decode('utf-8')
        except Exception as e:
            raise TokenGenerationException(f"Failed to generate token: {str(e)}")
        
    def verify_token(
        self,
        token: str,
        expected_token_type: str
    ) -> Dict[str, Any]:
        """
        Verify and decode JWT token.

        Args:
            token (str): Token to verify
            expected_token_type (str): Expected token type

        Returns:
            dict: Decoded token payload

        Raises:
            TokenVerificationException: For invalid or expired tokens
            TokenTypeMismatchException: When token type doesn't match
        """
        try:
            jwt_instance = JsonWebToken(algorithms=[self._algo])
            decoded_token = jwt_instance.decode(token, self.key_provider.public_key())
            decoded_token.validate()
            
            if decoded_token['token_use'] != expected_token_type:
                raise TokenTypeMismatchException()
                
            return decoded_token
        except TokenTypeMismatchException:
            raise
        except ExpiredTokenError:
            raise TokenVerificationException("Token has expired")
        except (DecodeError, InvalidTokenError):
            raise TokenVerificationException("Invalid token")
        except Exception as e:
            raise TokenVerificationException(f"Token verification failed: {str(e)}")
        
    def get_jwk_set(self) -> Dict[str, Any]:
        """
        Get the JWK set containing public key and metadata.

        Returns:
            dict: JWK set dictionary
        """
        try:
            key_set = self.key_provider.public_key().as_dict()
            key_set['alg'] = self._algo
            key_set['use'] = 'sig'
            return {"keys": [key_set]}
        except Exception as e:
            raise TokenGenerationException(f"Failed to generate JWK set: {str(e)}")