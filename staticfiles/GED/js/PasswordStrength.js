$(document).ready(function() {
$('#Password').keyup(function() {
$('#result').html(checkStrength($('#Password').val()))
})
function checkStrength(password) {
var strength = 0
if (password.length < 6 && password.length>0) {
$('#result').removeClass()
$('#result').addClass('short')
return 'Trop Court'
}
if (password.length > 7) strength += 1
// If password contains both lower and uppercase characters, increase strength value.
if (password.match(/([a-z].*[A-Z])|([A-Z].*[a-z])/)) strength += 1
// If it has numbers and characters, increase strength value.
if (password.match(/([a-zA-Z])/) && password.match(/([0-9])/)) strength += 1
// If it has one special character, increase strength value.
if (password.match(/([!,%,&,@,#,$,^,*,?,_,~])/)) strength += 1
// If it has two special characters, increase strength value.
if (password.match(/(.*[!,%,&,@,#,$,^,*,?,_,~].*[!,%,&,@,#,$,^,*,?,_,~])/)) strength += 1
// Calculated strength value, we can return messages
// If value is less than 2
if (strength < 2) {
$('#result').removeClass()
$('#result').addClass('weak')
return 'Faible'
} else if (strength == 2) {
$('#result').removeClass()
$('#result').addClass('good')
return 'Moyen'
} else {
$('#result').removeClass()
$('#result').addClass('strong')
return 'Fort'
}
}
});