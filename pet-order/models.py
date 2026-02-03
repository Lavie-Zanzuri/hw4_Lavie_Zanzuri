"""
Models for pet-order service
"""

class Purchase:
    """Purchase model"""
    def __init__(self, purchaser, pet_type, store=None, pet_name=None, purchase_id=None):
        self.purchaser = purchaser
        self.pet_type = pet_type
        self.store = store
        self.pet_name = pet_name
        self.purchase_id = purchase_id
    
    def to_dict(self):
        """Convert to dictionary"""
        result = {
            "purchaser": self.purchaser,
            "pet-type": self.pet_type,
            "purchase-id": self.purchase_id
        }
        
        if self.store is not None:
            result["store"] = self.store
        
        if self.pet_name is not None:
            result["pet-name"] = self.pet_name
        
        return result


class Transaction:
    """Transaction model for owner view"""
    def __init__(self, purchaser, pet_type, store, purchase_id):
        self.purchaser = purchaser
        self.pet_type = pet_type
        self.store = store
        self.purchase_id = purchase_id
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "purchaser": self.purchaser,
            "pet-type": self.pet_type,
            "store": self.store,
            "purchase-id": self.purchase_id
        }
