var mongoose = require('mongoose');
var Schema = mongoose.Schema;

var UserSchema = new Schema({
	name: String,
	privider:String,
	provider_id: {type: String, unique:true},
	photo: String,
	createdAt: {type: Date, default: Date.now}
});

var User = mongoose.model('User',UserSchema);