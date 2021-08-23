function nueva_categoria(form) {
    var x = document.getElementById("txtId_categoria");
    var sel = x.options[x.selectedIndex].id;
    var y = document.getElementById("categoria");
    if (sel == "nueva") {
        y.style.display = "block";
    }
    else {
        y.style.display = "none";
    }
}


function desplegar(id,display="block") {
    var x = document.getElementById(id);
    if (x.style.display === "none") {
        x.style.display = display;
    } else {
        x.style.display = "none";
    }
}
