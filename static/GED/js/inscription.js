var mail = document.getElementById("email");
mail.addEventListener("focus", function () {
	document.getElementById("aide").textContent = "format: @ept.sn";
});

var mail = document.getElementById("email");
mail.addEventListener("blur", function (e) {
	document.getElementById("aide").textContent = "";
});

/*---[a-zA-Z0-9] signifie qu'on autorise les lettres masjuscules comme minuscules ainsi que les chiffres---*/

if (/^[.-_a-zA-Z0-9]+@ept.sn$/.test(mail)){
	mail.addEventListener("focus", function () {
	document.getElementById("aide").textContent = "format: @ept.sn";
	});
};
