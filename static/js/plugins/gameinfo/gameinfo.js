function update_sql(){

    var opendata=new Array();
    var show=document.getElementsByName('subcheck');
    for(var i=0;i<show.length;i++){
        if(show[i].checked==true) {
            opendata[i] = show[i].value + '<br>';
        }
    }

    if(opendata.length == 0){
        $("#update-game-db").addClass('disabled');
        $("#update-log-db").addClass('disabled');
        $("#update-data-db").addClass('disabled');

    }else{
        $("#update-game-db").removeClass('disabled');
        $("#update-log-db").removeClass('disabled');
        $("#update-data-db").removeClass('disabled');
    }
	for(var i=0;i<opendata.length;i++){
        if(opendata[i] == "" || typeof(opendata[i]) == "undefined")
        {
                opendata.splice(i,1);
                i = i-1;
        }
    }
    $(".open_check_list").html(opendata);
}

function update_config(){

    var opendata=new Array();
    var show=document.getElementsByName('subcheck');
    for(var i=0;i<show.length;i++){
        if(show[i].checked==true) {
            opendata[i] = show[i].value + '<br>';
        }
    }

    if(opendata.length == 0){
        $("#update-game-config").addClass('disabled');
    }else{
        $("#update-game-config").removeClass('disabled');
    }
    
	for(var i=0;i<opendata.length;i++){
        if(opendata[i] == "" || typeof(opendata[i]) == "undefined")
        {
                opendata.splice(i,1);
                i = i-1;
        }
        }
    $(".open_check_list").html(opendata);
}

function update_file(){

    var opendata=new Array();
    var show=document.getElementsByName('subcheck');
    for(var i=0;i<show.length;i++){
            if(show[i].checked==true) {
                opendata[i] = show[i].value + '<br>';
            }
    }

    if(opendata.length == 0){
        $("#update-file-cold").addClass('disabled');
        $("#update-file-heat").addClass('disabled');
        $("#update-file-heatdb").addClass('disabled');


    }else{
        $("#update-file-cold").removeClass('disabled');
        $("#update-file-heat").removeClass('disabled');
        $("#update-file-heatdb").removeClass('disabled');
    }
	for(var i=0;i<opendata.length;i++){
        if(opendata[i] == "" || typeof(opendata[i]) == "undefined")
        {
                opendata.splice(i,1);
                i = i-1;
        }
    }
    $(".open_check_list").html(opendata);
}

function game_open(){
    var opendata=new Array();
    var show=document.getElementsByName('subcheck');
    for(var i=0;i<show.length;i++){
        if(show[i].checked==true){
        opendata[i]=show[i].value+'<br>';
        }
    }
    
	for(var i=0;i<opendata.length;i++){
        if(opendata[i] == "" || typeof(opendata[i]) == "undefined")
        {
                opendata.splice(i,1);
                i = i-1;
        }
    }
    document.getElementById("open_list").innerHTML=opendata;
}

function game_close(){
        var closedata=new Array();
        var show=document.getElementsByName('subcheck');

        for(var i=0;i<show.length;i++){
            if(show[i].checked==true){
            closedata[i]=show[i].value+'<br>';
        }
    }
	for(var i=0;i<closedata.length;i++){
                if(closedata[i] == "" || typeof(closedata[i]) == "undefined")
                {
                        closedata.splice(i,1);
                        i = i-1;
                }
        }
        document.getElementById("close_list").innerHTML=closedata;
}

function game_delete(){
        var closedata=new Array();
        var show=document.getElementsByName('subcheck');

        for(var i=0;i<show.length;i++){
            if(show[i].checked==true){
            closedata[i]=show[i].value+'<br>';
        }
    }
	for(var i=0;i<closedata.length;i++){
                if(closedata[i] == "" || typeof(closedata[i]) == "undefined")
                {
                        closedata.splice(i,1);
                        i = i-1;
                }
        }
        document.getElementById("delete_list").innerHTML=closedata;
}

function update_data(){
        var closedata=new Array();
        var show=document.getElementsByName('subcheck');

        for(var i=0;i<show.length;i++){
            if(show[i].checked==true){
            closedata[i]=show[i].value+'<br>';
        }
    }
	for(var i=0;i<closedata.length;i++){
                if(closedata[i] == "" || typeof(closedata[i]) == "undefined")
                {
                        closedata.splice(i,1);
                        i = i-1;
                }
        }
        document.getElementById("data_list").innerHTML=closedata;
}

function game_del(){
        var deldata=new Array();
        var show=document.getElementsByName('subcheck');
        
        for(var i=0;i<show.length;i++){
            if(show[i].checked==true){
            deldata[i]=show[i].value+'<br>';
        }
    }
	for(var i=0;i<deldata.length;i++){
                if(deldata[i] == "" || typeof(deldata[i]) == "undefined")
                {
                        deldata.splice(i,1);
                        i = i-1;
                }
        }
        document.getElementById("del_list").innerHTML=deldata;
}


function game_clear(){
        var deldata=new Array();
        var show=document.getElementsByName('subcheck');
        
        for(var i=0;i<show.length;i++){
            if(show[i].checked==true){
            deldata[i]=show[i].value+'<br>';
        }
    }
  for(var i=0;i<deldata.length;i++){
                if(deldata[i] == "" || typeof(deldata[i]) == "undefined")
                {
                        deldata.splice(i,1);
                        i = i-1;
                }
        }
        document.getElementById("clear_list").innerHTML=deldata;
}



function game_backup(){
        var deldata=new Array();
        var show=document.getElementsByName('subcheck');
        
        for(var i=0;i<show.length;i++){
            if(show[i].checked==true){
            deldata[i]=show[i].value+'<br>';
        }
    }
  for(var i=0;i<deldata.length;i++){
                if(deldata[i] == "" || typeof(deldata[i]) == "undefined")
                {
                        deldata.splice(i,1);
                        i = i-1;
                }
        }
        document.getElementById("backup_list").innerHTML=deldata;
}


function game_merge(){
        var deldata=new Array();
        var show=document.getElementsByName('subcheck');

        for(var i=0;i<show.length;i++){
            if(show[i].checked==true){
            	deldata[i]=show[i].value+'<br>';
        }
    }
  for(var i=0;i<deldata.length;i++){
                if(deldata[i] == "" || typeof(deldata[i]) == "undefined")
                {
                        deldata.splice(i,1);
                        i = i-1;
                }
        }
        document.getElementById("merge_list").innerHTML=deldata;
}

function start_nginx(){
    var opendata=new Array();
    var show=document.getElementsByName('subcheck');
    for(var i=0;i<show.length;i++){
        if(show[i].checked==true){
        opendata[i]=show[i].value+'<br>';
        }
    }

	for(var i=0;i<opendata.length;i++){
        if(opendata[i] == "" || typeof(opendata[i]) == "undefined")
        {
                opendata.splice(i,1);
                i = i-1;
        }
    }
    document.getElementById("start_nginx_list").innerHTML=opendata;
}

function stop_nginx(){
    var opendata=new Array();
    var show=document.getElementsByName('subcheck');
    for(var i=0;i<show.length;i++){
        if(show[i].checked==true){
        opendata[i]=show[i].value+'<br>';
        }
    }

	for(var i=0;i<opendata.length;i++){
        if(opendata[i] == "" || typeof(opendata[i]) == "undefined")
        {
                opendata.splice(i,1);
                i = i-1;
        }
    }
    document.getElementById("stop_nginx_list").innerHTML=opendata;
}

function restart_nginx(){
    var opendata=new Array();
    var show=document.getElementsByName('subcheck');
    for(var i=0;i<show.length;i++){
        if(show[i].checked==true){
        opendata[i]=show[i].value+'<br>';
        }
    }

	for(var i=0;i<opendata.length;i++){
        if(opendata[i] == "" || typeof(opendata[i]) == "undefined")
        {
                opendata.splice(i,1);
                i = i-1;
        }
    }
    document.getElementById("restart_nginx_list").innerHTML=opendata;
}

function restart_phpfpm(){
    var opendata=new Array();
    var show=document.getElementsByName('subcheck');
    for(var i=0;i<show.length;i++){
        if(show[i].checked==true){
        opendata[i]=show[i].value+'<br>';
        }
    }

	for(var i=0;i<opendata.length;i++){
        if(opendata[i] == "" || typeof(opendata[i]) == "undefined")
        {
                opendata.splice(i,1);
                i = i-1;
        }
    }
    document.getElementById("restart_phpfpm_list").innerHTML=opendata;
}