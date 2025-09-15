from django.db import models
from django.utils.translation import gettext_lazy as _
from approvals.models import Approval
from authentication.models import User

class BlockchainLog(models.Model):
    """
    Model to store the transaction hash of an approval logged on the blockchain.
    This serves as an off-chain reference to the immutable on-chain record.
    """
    approval = models.OneToOneField(Approval, on_delete=models.CASCADE, related_name='blockchain_log')
    transaction_hash = models.CharField(max_length=66) # 0x prefix + 64 hex characters
    logged_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_logged = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tx: {self.transaction_hash} for Approval #{self.approval.id}"

    class Meta:
        verbose_name = _('Blockchain Log')
        verbose_name_plural = _('Blockchain Logs')
        ordering = ['-date_logged']