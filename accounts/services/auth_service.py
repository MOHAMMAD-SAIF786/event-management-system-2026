"""
Modular Customer Authentication Service
Supports Local Django Auth and pluggable Third-Party OAuth2/SSO Providers (e.g. Google, GitHub, Apple, Firebase).
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, Any
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import transaction
from accounts.models import Customer


class BaseAuthProvider(ABC):
    """
    Abstract Base Class for all Authentication Providers.
    """

    @abstractmethod
    def authenticate(self, credentials: Dict[str, Any]) -> Optional[User]:
        """
        Authenticate user with provided credentials.
        Returns User object if successful, None otherwise.
        """
        pass

    @abstractmethod
    def register(self, data: Dict[str, Any]) -> Tuple[User, Customer]:
        """
        Register a new user and link/create Customer profile.
        Returns a tuple of (User, Customer).
        """
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Fetch a user instance by primary key.
        """
        pass


class LocalDjangoAuthProvider(BaseAuthProvider):
    """
    Standard Local Username/Email + Password Authentication Provider.
    """

    def authenticate(self, credentials: Dict[str, Any]) -> Optional[User]:
        login_input = credentials.get("username", "").strip()
        password = credentials.get("password", "")

        if not login_input or not password:
            return None

        username = login_input
        # Support login by email
        if "@" in login_input:
            user_obj = User.objects.filter(email__iexact=login_input).first()
            if user_obj:
                username = user_obj.username

        return authenticate(username=username, password=password)

    def register(self, data: Dict[str, Any]) -> Tuple[User, Customer]:
        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "")
        name = data.get("name", "").strip() or username
        phone = data.get("phone", "").strip()

        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=name
            )

            customer_phone = phone if phone else f"0000000000_{user.id}"
            customer, created = Customer.objects.get_or_create(
                phone=customer_phone,
                defaults={
                    "user": user,
                    "name": name,
                    "email": email,
                }
            )

            if not created and not customer.user:
                customer.user = user
                customer.name = name
                customer.email = email
                customer.save()

            return user, customer

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        try:
            return User.objects.get(pk=user_id, is_active=True)
        except User.DoesNotExist:
            return None


class OAuth2BaseProvider(BaseAuthProvider):
    """
    Base Provider for Third-Party OAuth2 Providers (Google, Apple, GitHub, Firebase, etc.).
    Subclasses only need to implement provider-specific token exchange and profile mapping.
    """

    def __init__(self, provider_name: str, client_id: str = "", client_secret: str = ""):
        self.provider_name = provider_name
        self.client_id = client_id
        self.client_secret = client_secret

    def get_authorization_url(self, redirect_uri: str, state: str = "") -> str:
        """
        Generate external OAuth redirect URL.
        """
        raise NotImplementedError("Subclasses must implement get_authorization_url")

    def exchange_code_for_profile(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Exchange auth code for user profile {email, name, provider_user_id, etc.}.
        """
        raise NotImplementedError("Subclasses must implement exchange_code_for_profile")

    def authenticate(self, credentials: Dict[str, Any]) -> Optional[User]:
        profile = credentials.get("profile")
        if not profile or not profile.get("email"):
            return None

        email = profile.get("email")
        user = User.objects.filter(email__iexact=email).first()
        return user

    def register(self, data: Dict[str, Any]) -> Tuple[User, Customer]:
        profile = data.get("profile", {})
        email = profile.get("email", "")
        name = profile.get("name", "") or profile.get("first_name", "OAuth User")
        username = profile.get("username") or email.split("@")[0]

        # Ensure unique username
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=name
            )
            user.set_unusable_password()
            user.save()

            customer, _ = Customer.objects.get_or_create(
                user=user,
                defaults={
                    "name": name,
                    "email": email,
                    "phone": f"oauth_{self.provider_name}_{user.id}",
                }
            )

            return user, customer

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        try:
            return User.objects.get(pk=user_id, is_active=True)
        except User.DoesNotExist:
            return None


class CustomerAuthManager:
    """
    Central registry and facade for customer authentication providers.
    """

    _providers: Dict[str, BaseAuthProvider] = {
        "local": LocalDjangoAuthProvider(),
    }

    @classmethod
    def register_provider(cls, name: str, provider: BaseAuthProvider) -> None:
        """
        Register a new authentication provider (e.g. 'google', 'firebase').
        """
        cls._providers[name] = provider

    @classmethod
    def get_provider(cls, name: str = "local") -> BaseAuthProvider:
        """
        Retrieve a registered authentication provider by name.
        """
        if name not in cls._providers:
            raise ValueError(f"Authentication provider '{name}' is not registered.")
        return cls._providers[name]

    @classmethod
    def authenticate(cls, provider_name: str = "local", **credentials) -> Optional[User]:
        """
        Authenticate via specified provider.
        """
        provider = cls.get_provider(provider_name)
        return provider.authenticate(credentials)

    @classmethod
    def register(cls, provider_name: str = "local", **data) -> Tuple[User, Customer]:
        """
        Register user via specified provider.
        """
        provider = cls.get_provider(provider_name)
        return provider.register(data)
