# region Import Packages

from Models.BaseModel.BaseModel import *
from Logix.DbManager.DbManager import db

# endregion

# region TestAuthentications Table

class TestAuthentications(BaseModel, db.Model):

    __tablename__ = "TestAuthentications"

    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserId = db.Column(db.String(300), unique=True)
    Email = db.Column(db.String(100), unique=True)
    Password = db.Column(db.String(300))
    Token = db.Column(db.String(300))
    ConfirmStatus = db.Column(db.Integer)
    Role = db.Column(db.String(100))
    Name = db.Column(db.String(30))
    Surname = db.Column(db.String(30))
    ImagePath = db.Column(db.String(500))
    CreatedBy = db.Column(db.String(300))
    CreatedAt = db.Column(db.String(30))
    ChangedBy = db.Column(db.String(300))
    ChangedAt = db.Column(db.String(30))
    Revision = db.Column(db.Integer)
    DeleteFlag = db.Column(db.Integer)

    def __init__(self, UserId, Email, Password, Token, ConfirmStatus, Role, Name, SurName, ImagePath, CreatedBy, CreatedAt, ChangedBy, ChangedAt, Revision, DeleteFlag):

        self.UserId = UserId
        self.Email = Email
        self.SubscriptionId = SubscriptionId
        self.SubscriptionName = SubscriptionName
        self.Password = Password
        self.Token = Token
        self.ConfirmStatus = ConfirmStatus
        self.Role = Role
        self.Name = Name
        self.Surname = SurName
        self.ImagePath = ImagePath
        self.CreatedBy = CreatedBy
        self.CreatedAt = CreatedAt
        self.ChangedBy = ChangedBy
        self.ChangedAt = ChangedAt
        self.Revision = Revision
        self.DeleteFlag = DeleteFlag

    def to_dict(self):
        
        return {prop: getattr(self, prop) for prop in dir(self) if not prop.startswith('_') and not callable(getattr(self, prop))}
    
# endregion
