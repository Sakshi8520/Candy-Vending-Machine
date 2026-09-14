from marshmallow import Schema, fields, validate

class CandyPurchaseSchema(Schema):
	candy_id = fields.Integer(required=True)
	quantity = fields.Integer(required=True,validate=validate.Range(min=1))

class CandySchema(Schema):
	candy_name = fields.Str()
	price = fields.Integer()
	stock = fields.Integer()
	id = fields.Integer()

class UserSchema(Schema):
	username = fields.String(required=True)
	email = fields.Email(required=True)