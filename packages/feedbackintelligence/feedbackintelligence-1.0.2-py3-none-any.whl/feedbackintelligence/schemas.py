from pydantic import BaseModel, model_validator
from typing import Literal


class Context(BaseModel):
    context_id: int | None = None
    text: str | None = None

    @model_validator(mode='before')
    def validate_context(cls, values):
        id_value, context_value = values.get('context_id'), values.get('text')
        if id_value is None and context_value is None:
            raise ValueError('Either text or context_id must be provided')
        return values

    def to_dict(self):
        data = {}
        if self.context_id is not None:
            data['context_id'] = self.context_id
        if self.text is not None:
            data['text'] = self.text

        return data


class Feedback(BaseModel):
    thumbs_up: int | None = None
    rating: float | None = None
    message: str | None = None

    @model_validator(mode='before')
    def validate_feedback(cls, values):
        thumbs_up, rating, message = values.get('thumbs_up'), values.get('rating'), values.get('message')
        if thumbs_up is None and rating is None and message is None:
            raise ValueError('Either thumbs_up or rating or message must be provided for Feedback')
        return values

    def to_dict(self):
        data = {}
        if self.thumbs_up is not None:
            data['thumbs_up'] = self.thumbs_up
        if self.rating is not None:
            data['rating'] = self.rating
        if self.message is not None:
            data['message'] = self.message

        return data


class Message(BaseModel):
    role: Literal['human', 'ai']
    text: str
    message_id: str | None = None
    prompt: str | None = None
    date: str | None = None
    context: Context | None = None
    feedback: Feedback | None = None

    def to_dict(self):
        data = {
            'role': self.role,
            'text': self.text,
        }
        if self.prompt is not None:
            data.update({'prompt': self.prompt})
        if self.date is not None:
            data.update({'date': self.date})
        if self.context is not None:
            data.update({'context': self.context.to_dict()})
        if self.feedback is not None:
            data.update({'feedback': self.feedback.to_dict()})
        if self.message_id is not None:
            data.update({'message_id': self.message_id})

        return data
