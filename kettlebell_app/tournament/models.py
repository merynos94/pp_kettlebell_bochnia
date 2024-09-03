from django.db import models
from django.db.models import Max, Sum

AVAILABLE_DISCIPLINES = [
    ("snatch", "Snatch"),
    ("tgu", "Turkish Get-Up"),
    ("see_saw_press", "See Saw Press"),
    ("kb_squat", "Kettlebell Squat"),
    ("pistols_squat", "Pistols Squat"),
]


class SportClub(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    disciplines = models.JSONField(default=list)

    def __str__(self):
        return self.name

    def set_disciplines(self, disciplines):
        valid_disciplines = [d[0] for d in AVAILABLE_DISCIPLINES]
        self.disciplines = [d for d in disciplines if d in valid_disciplines]
        self.save()

    def get_disciplines(self):
        return self.disciplines


class Player(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    weight = models.FloatField(null=True, blank=True, default=0)
    club = models.ForeignKey(SportClub, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category)

    snatch_kettlebell_weight = models.FloatField(null=True, blank=True, default=0)
    snatch_repetitions = models.IntegerField(null=True, blank=True, default=0)

    tgu_weight_1 = models.FloatField(null=True, blank=True, default=0)
    tgu_weight_2 = models.FloatField(null=True, blank=True, default=0)
    tgu_weight_3 = models.FloatField(null=True, blank=True, default=0)

    see_saw_press_weight_left_1 = models.FloatField(null=True, blank=True, default=0)
    see_saw_press_weight_left_2 = models.FloatField(null=True, blank=True, default=0)
    see_saw_press_weight_left_3 = models.FloatField(null=True, blank=True, default=0)
    see_saw_press_weight_right_1 = models.FloatField(null=True, blank=True, default=0)
    see_saw_press_weight_right_2 = models.FloatField(null=True, blank=True, default=0)
    see_saw_press_weight_right_3 = models.FloatField(null=True, blank=True, default=0)

    kb_squat_weight_left_1 = models.FloatField(null=True, blank=True, default=0)
    kb_squat_weight_left_2 = models.FloatField(null=True, blank=True, default=0)
    kb_squat_weight_left_3 = models.FloatField(null=True, blank=True, default=0)
    kb_squat_weight_right_1 = models.FloatField(null=True, blank=True, default=0)
    kb_squat_weight_right_2 = models.FloatField(null=True, blank=True, default=0)
    kb_squat_weight_right_3 = models.FloatField(null=True, blank=True, default=0)

    pistol_squat_weight_1 = models.FloatField(null=True, blank=True, default=0)
    pistol_squat_weight_2 = models.FloatField(null=True, blank=True, default=0)
    pistol_squat_weight_3 = models.FloatField(null=True, blank=True, default=0)
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
            self._update_best_kb_squat_result()
            self._update_best_see_saw_press_result()
            self._update_pistol_squat_result()
            self._update_overall_result()
        finally:
            self._updating_results = False

    def _update_overall_result(self):
        overall_result, created = OverallResult.objects.get_or_create(player=self)

        for discipline, _ in AVAILABLE_DISCIPLINES:
            points = 0
            for category in self.categories.all():
                if discipline in category.get_disciplines():
                    result = getattr(self, f"{discipline}result_set").first()
                    if result:
                        points += result.position if result.position else 0
            setattr(overall_result, f"{discipline}_points", points)

        overall_result.calculate_total_points()
        overall_result.save()

    def _update_snatch_result(self):
        snatch_result, _ = SnatchResult.objects.get_or_create(player=self)
        snatch_result.result = round(self.snatch_results() or 0, 1)
        snatch_result.save()

    def _update_tgu_result(self):
        tgu_result, _ = TGUResult.objects.get_or_create(player=self)
        tgu_result.result_1 = self.tgu_weight_1 or 0
        tgu_result.result_2 = self.tgu_weight_2 or 0
        tgu_result.result_3 = self.tgu_weight_3 or 0
        tgu_result.save()

    def _update_pistol_squat_result(self):
        pistol_squat_result, _ = PistolSquatResult.objects.get_or_create(player=self)
        pistol_squat_result.result_1 = self.pistol_squat_weight_1 or 0
        pistol_squat_result.result_2 = self.pistol_squat_weight_2 or 0
        pistol_squat_result.result_3 = self.pistol_squat_weight_3 or 0
        pistol_squat_result.save()

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
        for side in ["left", "right"]:
            for attempt in range(1, 4):
                setattr(
                    kb_squat_result,
                    f"result_{side}_{attempt}",
                    self.kb_squat_body_percent_weight(side, attempt),
                )
        kb_squat_result.save()

    def _update_best_kb_squat_result(self):
        best_kb_squat_result, _ = BestKBSquatResult.objects.get_or_create(player=self)
        best_kb_squat_result.update_best_result()

    def _update_best_see_saw_press_result(self):
        best_see_saw_result, _ = BestSeeSawPressResult.objects.get_or_create(
            player=self
        )
        best_see_saw_result.update_best_results()

    # def _update_overall_result(self):
    #     overall_result, created = OverallResult.objects.get_or_create(player=self)
    #
    #     # Snatch
    #     snatch_result = self.snatchresult_set.first()
    #     overall_result.snatch_points = snatch_result.position if snatch_result else 0
    #
    #     # TGU
    #     tgu_result = self.tguresult_set.first()
    #     overall_result.tgu_points = tgu_result.position if tgu_result else 0
    #
    #     # See Saw Press
    #     see_saw_result = self.seesawpressresult_set.first()
    #     overall_result.see_saw_press_points = (
    #         see_saw_result.position if see_saw_result else 0
    #     )
    #
    #     # KB Squat
    #     kb_squat_result = self.kbsquatresult_set.first()
    #     overall_result.kb_squat_points = (
    #         kb_squat_result.position if kb_squat_result else 0
    #     )
    #
    #     # Pistols Squat
    #     pistol_squat_result = self.pistolsquatresult_set.first()
    #     overall_result.pistol_squat_points = (
    #         pistol_squat_result.position if pistol_squat_result else 0
    #     )
    #
    #     # Calculate total points
    #     overall_result.calculate_total_points()
    #     overall_result.save()

    def get_max_pistol_squat_weight(self):
        return max(
            self.pistol_squat_weight_1 or 0,
            self.pistol_squat_weight_2 or 0,
            self.pistol_squat_weight_3 or 0,
        )

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
        max_tgu_weight = max(
            self.tgu_weight_1 or 0, self.tgu_weight_2 or 0, self.tgu_weight_3 or 0
        )
        return (
            (max_tgu_weight / self.weight) * 100
            if max_tgu_weight and self.weight
            else None
        )

    def get_max_tgu_weight(self):
        return max(
            self.tgu_weight_1 or 0, self.tgu_weight_2 or 0, self.tgu_weight_3 or 0
        )

    def see_saw_press_body_percent_weight_left(self, attempt):
        weight = getattr(self, f"see_saw_press_weight_left_{attempt}")
        return (((weight * 3) / self.weight) * 100) if weight and self.weight else None

    def see_saw_press_body_percent_weight_right(self, attempt):
        weight = getattr(self, f"see_saw_press_weight_right_{attempt}")
        return (((weight * 3) / self.weight) * 100) if weight and self.weight else None


class SnatchResult(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    result = models.FloatField(null=True, blank=True)  # Zezwalamy na wartości null
    position = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.player} - Snatch: {self.result if self.result is not None else 'N/A'}"


class TGUResult(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    result_1 = models.FloatField(default=0)
    result_2 = models.FloatField(default=0)
    result_3 = models.FloatField(default=0)
    position = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.player} - TGU Results"

    def get_max_result(self):
        return max(self.result_1 or 0, self.result_2 or 0, self.result_3 or 0)

    def calculate_bw_percentage(self):
        if self.player.weight:
            max_result = self.get_max_result()
            return (max_result / self.player.weight) * 100
        return 0


class PistolSquatResult(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    result_1 = models.FloatField(default=0)
    result_2 = models.FloatField(default=0)
    result_3 = models.FloatField(default=0)
    position = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.player} - Pistol Squat Results"

    def get_max_result(self):
        return max(self.result_1 or 0, self.result_2 or 0, self.result_3 or 0)

    def calculate_bw_percentage(self):
        if self.player.weight:
            max_result = self.get_max_result()
            return (max_result / self.player.weight) * 100
        return 0


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
            (self.result_left_1 + self.result_right_1),
            (self.result_left_2 + self.result_right_2),
            (self.result_left_3 + self.result_right_3),
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
    result_left_1 = models.FloatField(default=0)
    result_right_1 = models.FloatField(default=0)
    result_left_2 = models.FloatField(default=0)
    result_right_2 = models.FloatField(default=0)
    result_left_3 = models.FloatField(default=0)
    result_right_3 = models.FloatField(default=0)
    position = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.player} - KB Squat Results"

    def get_max_result(self):
        valid_attempts = [
            self.result_left_1 + self.result_right_1
            if self.result_left_1 > 0 and self.result_right_1 > 0
            else 0,
            self.result_left_2 + self.result_right_2
            if self.result_left_2 > 0 and self.result_right_2 > 0
            else 0,
            self.result_left_3 + self.result_right_3
            if self.result_left_3 > 0 and self.result_right_3 > 0
            else 0,
        ]
        return max(valid_attempts)

    def get_attempt_result(self, attempt_number):
        left = getattr(self, f"result_left_{attempt_number}")
        right = getattr(self, f"result_right_{attempt_number}")
        return max(left, right) if left > 0 and right > 0 else 0


class BestKBSquatResult(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE)
    best_result = models.FloatField(default=0)

    def update_best_result(self):
        kb_squat_result = self.player.kbsquatresult_set.first()
        if kb_squat_result:
            self.best_result = kb_squat_result.get_max_result()
            self.save()

    def __str__(self):
        return f"{self.player} - Best KB Squat: {self.best_result}"


class OverallResult(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE)
    snatch_points = models.FloatField(default=0)
    tgu_points = models.FloatField(default=0)
    see_saw_press_points = models.FloatField(default=0)
    kb_squat_points = models.FloatField(default=0)
    pistol_squat_points = models.FloatField(default=0)
    tiebreak_points = models.FloatField(default=0)
    total_points = models.FloatField(default=0)
    final_position = models.IntegerField(null=True, blank=True)

    def calculate_total_points(self):
        category_disciplines = self.player.categories.first().get_disciplines()
        self.total_points = sum([
            getattr(self, f"{discipline}_points")
            for discipline in ['snatch', 'tgu', 'see_saw_press', 'kb_squat', 'pistols_squat']
            if discipline in category_disciplines
        ]) - (0.5 if self.player.tiebreak else 0)
        self.tiebreak_points = -0.5 if self.player.tiebreak else 0

        # Upewniamy się, że żadne pole nie jest None
        self.snatch_points = self.snatch_points or 0
        self.tgu_points = self.tgu_points or 0
        self.see_saw_press_points = self.see_saw_press_points or 0
        self.kb_squat_points = self.kb_squat_points or 0
        self.pistol_squat_points = self.pistol_squat_points or 0

    def save(self, *args, **kwargs):
        self.calculate_total_points()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.player} - Total: {self.total_points:.1f}"
