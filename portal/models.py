import datetime 

from django.db import models
from django.utils import timezone

# Create your models here.

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    def __str__(self):
        return self.question_text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

class Submitter(models.Model):
    name = models.CharField(max_length=200)
    # Probably want to store precomputed statistics
    # in this model, but leaving it simple for now.

    def __str__(self):
        return self.name

class WordleSubmission(models.Model):
    submission_text = models.CharField(max_length=200)
    submitter = models.ForeignKey(Submitter, on_delete=models.CASCADE)
    date_submitted = models.DateTimeField(auto_now_add=True)
    wordle_number = models.IntegerField()

    num_guesses = models.IntegerField() # how many out of 6
    invalid = models.IntegerField() # num black blocks
    valid_wrong_position = models.IntegerField() # num yellow blocks
    # NOTE: Need to ignore the final line in the wordle input
    # if it's the correct word, cause that'll inflate this
    # count by counting all greens in a correct answer, which
    # I don't think we want.
    valid_right_position = models.IntegerField() # num green blocks

    # EMOJI REACTIONS
    sad_reactions = models.IntegerField(default=0)
    mind_blown_reactions = models.IntegerField(default=0)
    wow_reactions = models.IntegerField(default=0)
    clap_reactions = models.IntegerField(default=0)
    monkey_reactions = models.IntegerField(default=0)

    @property
    def reaction_list(self):
        dc = self.__dict__
        reaction_list = []
        for key in dc.keys():
            if 'reaction' in key and dc[key] != 0:
                if 'sad' in key:
                    reaction_list.append('😢' + str(dc[key]))
                if 'mind' in key:
                    reaction_list.append('🤯' + str(dc[key]))
                if 'wow' in key:
                    reaction_list.append('😮' + str(dc[key]))
                if 'clap' in key:
                    reaction_list.append('👏' + str(dc[key]))
                if 'monkey' in key:
                    reaction_list.append('🦧' + str(dc[key]))

        return reaction_list

    def __str__(self):
        return f"\
        {self.submitter.name}\
        {self.wordle_number}\
        {self.num_guesses}\
        {self.invalid}\
        {self.valid_wrong_position}\
        {self.valid_right_position}"

