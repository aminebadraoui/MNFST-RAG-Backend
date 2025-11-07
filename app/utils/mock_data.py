"""
Mock data generator for testing and development
"""
from datetime import datetime, timedelta
from uuid import uuid4
import random
from typing import List, Optional

from app.models.user import User, UserRole
from app.models.tenant import Tenant
from app.models.document import Document, DocumentStatus
from app.models.social import SocialLink, SocialPlatform
from app.models.chat import Session, Message, MessageRole


class MockDataGenerator:
    """Generate mock data for testing and development"""
    
    @staticmethod
    def generate_id() -> str:
        """Generate a unique ID"""
        return str(uuid4())
    
    @staticmethod
    def generate_user(role: UserRole = UserRole.USER, tenant_id: Optional[str] = None) -> User:
        """Generate a mock user"""
        if tenant_id is None:
            tenant_id = MockDataGenerator.generate_id()
            
        email_map = {
            UserRole.SUPERADMIN: "superadmin@ragchat.com",
            UserRole.TENANT_ADMIN: "admin@tenant.com",
            UserRole.USER: "user@tenant.com"
        }
        
        name_map = {
            UserRole.SUPERADMIN: "Super Admin",
            UserRole.TENANT_ADMIN: "Tenant Admin",
            UserRole.USER: "Regular User"
        }
        
        return User(
            id=MockDataGenerator.generate_id(),
            email=email_map.get(role, "user@example.com"),
            name=name_map.get(role, "Mock User"),
            role=role,
            tenant_id=None if role == UserRole.SUPERADMIN else tenant_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_login=datetime.utcnow() - timedelta(hours=random.randint(1, 24))
        )
    
    @staticmethod
    def generate_tenant() -> Tenant:
        """Generate a mock tenant"""
        return Tenant(
            id=MockDataGenerator.generate_id(),
            name=f"Mock Tenant {random.randint(1, 100)}",
            slug=f"mock-tenant-{random.randint(1, 100)}",
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 365)),
            updated_at=datetime.utcnow() - timedelta(hours=random.randint(1, 24))
        )
    
    @staticmethod
    def generate_document(tenant_id: Optional[str] = None, user_id: Optional[str] = None) -> Document:
        """Generate a mock document"""
        if tenant_id is None:
            tenant_id = MockDataGenerator.generate_id()
        if user_id is None:
            user_id = MockDataGenerator.generate_id()
            
        file_types = [
            {"name": "document.pdf", "mime": "application/pdf", "size": 1024000},
            {"name": "report.docx", "mime": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "size": 2048000},
            {"name": "presentation.pptx", "mime": "application/vnd.openxmlformats-officedocument.presentationml.presentation", "size": 3072000},
            {"name": "spreadsheet.xlsx", "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "size": 1536000},
            {"name": "image.png", "mime": "image/png", "size": 512000}
        ]
        
        file_type = random.choice(file_types)
        status = random.choice(list(DocumentStatus))
        
        return Document(
            id=MockDataGenerator.generate_id(),
            filename=f"{MockDataGenerator.generate_id()}_{file_type['name']}",
            original_name=file_type["name"],
            size=file_type["size"] + random.randint(0, 100000),
            mime_type=file_type["mime"],
            status=status,
            tenant_id=tenant_id,
            user_id=user_id,
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            updated_at=datetime.utcnow() - timedelta(hours=random.randint(1, 24)),
            processed_at=datetime.utcnow() - timedelta(hours=random.randint(1, 12)) if status == DocumentStatus.PROCESSED else None,
            error="Processing failed due to corrupted file" if status == DocumentStatus.ERROR else None
        )
    
    @staticmethod
    def generate_social_link(tenant_id: Optional[str] = None) -> SocialLink:
        """Generate a mock social link"""
        if tenant_id is None:
            tenant_id = MockDataGenerator.generate_id()
            
        platforms = list(SocialPlatform)
        urls = [
            "https://twitter.com/example",
            "https://facebook.com/example",
            "https://linkedin.com/company/example",
            "https://instagram.com/example",
            "https://youtube.com/c/example"
        ]
        
        return SocialLink(
            id=MockDataGenerator.generate_id(),
            url=random.choice(urls),
            platform=random.choice(platforms),
            tenant_id=tenant_id,
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            updated_at=datetime.utcnow() - timedelta(hours=random.randint(1, 24))
        )
    
    @staticmethod
    def generate_session(user_id: Optional[str] = None) -> Session:
        """Generate a mock chat session"""
        if user_id is None:
            user_id = MockDataGenerator.generate_id()
            
        return Session(
            id=MockDataGenerator.generate_id(),
            title=f"Chat Session {random.randint(1, 100)}",
            user_id=user_id,
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 7)),
            updated_at=datetime.utcnow() - timedelta(hours=random.randint(1, 24))
        )
    
    @staticmethod
    def generate_message(session_id: Optional[str] = None) -> Message:
        """Generate a mock message"""
        if session_id is None:
            session_id = MockDataGenerator.generate_id()
            
        user_messages = [
            "What is the capital of France?",
            "Explain quantum computing",
            "How does photosynthesis work?",
            "What are the benefits of renewable energy?",
            "Can you help me understand machine learning?"
        ]
        
        assistant_messages = [
            "The capital of France is Paris. It's known for its art, fashion, gastronomy and culture.",
            "Quantum computing is a revolutionary computing paradigm that uses quantum mechanics phenomena...",
            "Photosynthesis is the process by which plants convert sunlight, water, and carbon dioxide...",
            "Renewable energy offers numerous benefits including reduced greenhouse gas emissions...",
            "Machine learning is a subset of artificial intelligence that enables systems to learn..."
        ]
        
        is_user = random.choice([True, False])
        
        return Message(
            id=MockDataGenerator.generate_id(),
            session_id=session_id,
            content=random.choice(user_messages if is_user else assistant_messages),
            role=MessageRole.USER if is_user else MessageRole.ASSISTANT,
            timestamp=datetime.utcnow() - timedelta(minutes=random.randint(1, 1440))
        )
    
    @staticmethod
    def generate_users(count: int = 5, role: UserRole = UserRole.USER, tenant_id: Optional[str] = None) -> List[User]:
        """Generate multiple mock users"""
        return [MockDataGenerator.generate_user(role, tenant_id) for _ in range(count)]
    
    @staticmethod
    def generate_tenants(count: int = 5) -> List[Tenant]:
        """Generate multiple mock tenants"""
        return [MockDataGenerator.generate_tenant() for _ in range(count)]
    
    @staticmethod
    def generate_documents(count: int = 5, tenant_id: Optional[str] = None, user_id: Optional[str] = None) -> List[Document]:
        """Generate multiple mock documents"""
        return [MockDataGenerator.generate_document(tenant_id, user_id) for _ in range(count)]
    
    @staticmethod
    def generate_social_links(count: int = 3, tenant_id: Optional[str] = None) -> List[SocialLink]:
        """Generate multiple mock social links"""
        return [MockDataGenerator.generate_social_link(tenant_id) for _ in range(count)]
    
    @staticmethod
    def generate_sessions(count: int = 5, user_id: Optional[str] = None) -> List[Session]:
        """Generate multiple mock chat sessions"""
        return [MockDataGenerator.generate_session(user_id) for _ in range(count)]
    
    @staticmethod
    def generate_messages(count: int = 10, session_id: Optional[str] = None) -> List[Message]:
        """Generate multiple mock messages"""
        return [MockDataGenerator.generate_message(session_id) for _ in range(count)]