from django.db import models
from django.utils.translation import gettext_lazy as _

class Visit(models.Model):
    page_url   = models.CharField(_("Page URL"), max_length=200)
    visit_time = models.DateTimeField(_("Visit Time"), auto_now_add=True)
    ip_address = models.GenericIPAddressField(_("IP Address"))

    class Meta:
        verbose_name = _("Visit")
        verbose_name_plural = _("Visits")
        ordering = ['-visit_time']

    def __str__(self):
        return f"Visit to {self.page_url} at {self.visit_time} by {self.ip_address}"
