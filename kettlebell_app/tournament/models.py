from django.db import models
from django.db.models import Max, Sum


class SportClub(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    weight = models.FloatField(null=True, blank=True, default=0)
    club = models.ForeignKey(SportClub, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category)

    snatch_kettlebell_weight = models.FloatField(null=True, blank=True)
    snatch_repetitions = models.IntegerField(null=True, blank=True)

    tgu_weight = models.FloatField(null=True, blank=True)

    see_saw_press_weight_left_1 = models.FloatField(null=True, blank=True, default=0)
    see_saw_press_weight_left_2 = models.FloatField(null=True, blank=True, default=0)
    see_saw_press_weight_left_3 = models.FloatField(null=True, blank=True, default=0)
    see_saw_press_weight_right_1 = models.FloatField(null=True, blank=True, default=0)
    see_saw_press_weight_right_2 = models.FloatField(null=True, blank=True, default=0)
    see_saw_press_weight_right_3 = models.FloatField(null=True, blank=True, default=0)

    kb_squat_weight = models.FloatField(null=True, blank=True)

    tiebreak = models.BooleanField(default=False)

    _updating_results = False

    def update_results(self):
        if self._updating_results:
            return
        self._updating_results = True
        try:
            self._update_snatch_result()
            self._update_tgu_result()
            self._update_see_saw_press_result()
            self._update_kb_squat_result()
            self._update_best_see_saw_press_result()
            self._update_overall_result()
        finally:
            self._updating_results = False

    def _update_snatch_result(self):
        snatch_result, _ = SnatchResult.objects.get_or_create(player=self)
        snatch_result.result = round(self.snatch_results() or 0, 1)
        snatch_result.save()

    def _update_tgu_result(self):
        tgu_result, _ = TGUResult.objects.get_or_create(player=self)
        tgu_result.result = round(self.tgu_body_percent_weight() or 0, 1)
        tgu_result.save()

    def _update_see_saw_press_result(self):
        see_saw_result, _ = SeeSawPressResult.objects.get_or_create(player=self)
        for side in ["left", "right"]:
            for attempt in range(1, 4):
                setattr(
                    see_saw_result,
                    f"result_{side}_{attempt}",
                    round(
                        getattr(self, f"see_saw_press_body_percent_weight_{side}")(
                            attempt
                        )
                        or 0,
                        1,
                    ),
                )
        see_saw_result.save()

    def _update_kb_squat_result(self):
        kb_squat_result, _ = KBSquatResult.objects.get_or_create(player=self)
        kb_squat_result.result = round(self.kb_squat_body_percent_weight() or 0, 1)
        kb_squat_result.save()

    def _update_best_see_saw_press_result(self):
        best_see_saw_result, _ = BestSeeSawPressResult.objects.get_or_create(
            player=self
        )
        best_see_saw_result.update_best_results()

    def _update_overall_result(self):
        overall_result, _ = OverallResult.objects.get_or_create(player=self)
        overall_result.snatch_points = round(
            self.snatchresult_set.aggregate(Sum("result"))["result__sum"] or 0, 1
        )
        overall_result.tgu_points = round(
            self.tguresult_set.aggregate(Sum("result"))["result__sum"] or 0, 1
        )
        best_see_saw_result = self.bestseesawpressresult
        overall_result.see_saw_press_points = round(
            best_see_saw_result.best_left + best_see_saw_result.best_right, 1
        )
        overall_result.kb_squat_points = round(
            self.kbsquatresult_set.aggregate(Sum("result"))["result__sum"] or 0, 1
        )
        overall_result.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self._updating_results:
            self.update_results()

    def __str__(self):
        return f"{self.name} {self.surname}"

    def snatch_results(self):
        if self.snatch_kettlebell_weight and self.snatch_repetitions:
            return self.snatch_kettlebell_weight * self.snatch_repetitions
        return None

    def tgu_body_percent_weight(self):
        return (
            (self.tgu_weight / self.weight) if self.tgu_weight and self.weight else None
        )

    def see_saw_press_body_percent_weight_left(self, attempt):
        weight = getattr(self, f"see_saw_press_weight_left_{attempt}")
        return (((weight * 3) / self.weight) * 100) if weight and self.weight else None

    def see_saw_press_body_percent_weight_right(self, attempt):
        weight = getattr(self, f"see_saw_press_weight_right_{attempt}")
        return (((weight * 3) / self.weight) * 100) if weight and self.weight else None

    def kb_squat_body_percent_weight(self):
        return (
            (self.kb_squat_weight / self.weight)
            if self.kb_squat_weight and self.weight
            else None
        )


class SnatchResult(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    result = models.FloatField(null=True, blank=True)  # Zezwalamy na wartości null
    position = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.player} - Snatch: {self.result if self.result is not None else 'N/A'}"


class TGUResult(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    result = models.FloatField(null=True, blank=True)  # Zezwalamy na wartości null
    position = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return (
            f"{self.player} - TGU: {self.result if self.result is not None else 'N/A'}"
        )


class SeeSawPressResult(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    result_left_1 = models.FloatField(default=0)
    result_right_1 = models.FloatField(default=0)
    result_left_2 = models.FloatField(default=0)
    result_right_2 = models.FloatField(default=0)
    result_left_3 = models.FloatField(default=0)
    result_right_3 = models.FloatField(default=0)
    position = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.player} - See Saw Press Results"

    def get_attempt_result(self, attempt_number):
        left = getattr(self, f"result_left_{attempt_number}")
        right = getattr(self, f"result_right_{attempt_number}")
        return (left * 3) + (right * 3) if left > 0 and right > 0 else 0

    def get_max_result(self):
        return max(
            self.get_attempt_result(1),
            self.get_attempt_result(2),
            self.get_attempt_result(3),
        )


class BestSeeSawPressResult(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE)
    best_left = models.FloatField(default=0)
    best_right = models.FloatField(default=0)

    def update_best_results(self):
        see_saw_result = self.player.seesawpressresult_set.first()
        if see_saw_result:
            self.best_left = max(
                see_saw_result.result_left_1,
                see_saw_result.result_left_2,
                see_saw_result.result_left_3,
            )
            self.best_right = max(
                see_saw_result.result_right_1,
                see_saw_result.result_right_2,
                see_saw_result.result_right_3,
            )
            self.save()

    def __str__(self):
        return f"{self.player} - Best See Saw Press: Left {self.best_left}, Right {self.best_right}"


class KBSquatResult(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    result = models.FloatField(null=True, blank=True)  # Zezwalamy na wartości null
    position = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.player} - KB Squat: {self.result if self.result is not None else 'N/A'}"


class OverallResult(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE)
    snatch_points = models.FloatField(default=0)
    tgu_points = models.FloatField(default=0)
    see_saw_press_points = models.FloatField(default=0)
    kb_squat_points = models.FloatField(default=0)
    tiebreak_points = models.FloatField(default=0)
    total_points = models.FloatField(default=0)
    final_position = models.IntegerField(null=True, blank=True)

    def calculate_total_points(self):
        self.total_points = round(
            self.snatch_points
            + self.tgu_points
            + self.see_saw_press_points
            + self.kb_squat_points
            - (0.5 if self.player.tiebreak else 0),
            1,
        )
        self.tiebreak_points = -0.5 if self.player.tiebreak else 0

    def save(self, *args, **kwargs):
        self.calculate_total_points()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.player} - Total: {self.total_points:.1f}"
