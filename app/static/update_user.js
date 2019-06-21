
var i = 0;
var users = ["elf_legolas", "gnome_gimlie", "master_bombur"];

function update_user() {
	document.getElementById("pass_field").value = 'qwer'
	document.getElementById("user_field").value = users[i++];
	i = i % 3;
}





