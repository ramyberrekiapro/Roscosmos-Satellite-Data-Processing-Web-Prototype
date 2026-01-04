from django.db import models


class Images(models.Model):
    img = models.FileField(null=False, upload_to='images/')
    png = models.FileField(null=True, blank=True, upload_to='images/png/')
    name = models.CharField(null=True, max_length=255)
    min_lon = models.FloatField(null=True, blank=True)
    min_lat = models.FloatField(null=True, blank=True)
    max_lon = models.FloatField(null=True, blank=True)
    max_lat = models.FloatField(null=True, blank=True)

    def __str__(self):
        full_img_name = str(self.img.name)
        if '/' in full_img_name:
            img_name = list(full_img_name.rpartition('/'))
            immg= img_name.pop()
            print(immg)
            self.img.name = immg
            return immg
        else:
            return full_img_name