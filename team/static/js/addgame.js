function chk(input, wl){
	var chbox;
	if(wl == 0){
		chbox = document.getElementById("chbox_win");
	}
	else{
		chbox = document.getElementById("chbox_lose");
	}

	for(var i=0; i<chbox.length; i++) {
		if(chbox[i].checked == true){
			chbox[i].checked = false;
			if(i < 5){
				deterpchange(0, i+1);
			}
			else{
				deterpchange(1, i-4);
			}
		}
	}
	if(input.value <= 5){
		for(var i = 0; i < 5; i++){
			if(document.gameform.winner[i].checked == true){
				document.gameform.winner[i].checked = false;
				deterpchange(0, i+1);
			}
			if(document.gameform.loser[i].checked == true){
				document.gameform.loser[i].checked = false;
				deterpchange(0, i+1);
			}
		}
	}
	else{
		for(var i = 5; i < 10; i++){
			if(document.gameform.winner[i].checked == true){
				document.gameform.winner[i].checked = false;
				deterpchange(1, i-4);
			}
			if(document.gameform.loser[i].checked == true){
				document.gameform.loser[i].checked = false;
				deterpchange(1, i-4);
			}
		}
	}
	input.checked = true;
}