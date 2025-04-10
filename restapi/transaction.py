from .models import TransactionPercentage
from django.shortcuts import get_object_or_404
from decimal import Decimal


class Transaction:
    def __init__(self, vendor, customer, amount):
        self.vendor = vendor
        self.customer = customer
        self.amount = amount
        
    def pay(self):
        if self.customer.withdraw(self.amount):
            return True
        return False
    

class TransferFunds:
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = Decimal(amount)
        self.real_amount = amount

    def payment(self):
        if self.sender.withdraw(self.amount):
            self.recipient.deposit(self.real_amount)
            return True
        return False