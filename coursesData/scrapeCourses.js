classObs = [];
tables = document.getElementsByClassName("table_default");
mytable = tables[tables.length - 1];
classlines = mytable.getElementsByTagName("a");

for (e of classlines) {
  if (e.onclick) {
    courseID = e.getAttribute("onclick").substring("showCourse('35', '".length, "showCourse('35', '287611".length);
    txt = e.getAttribute("title").split(' - ');
    subNum = txt[0];
    desc = txt[1].substring(0, txt[1].length - "   opens a new window".length);

    classObs.push({
      "courseID": courseID,
      "subNum": subNum,
      "desc": desc
    }); // add data from lines to classobj
  }
}
console.log(classObs[classObs.length -1]);
console.log(mytable.getElementsByTagName("span")[0].firstChild.textContent);

filename = `Page_${mytable.getElementsByTagName("span")[0].firstChild.textContent}`;

function download(content, fileName, contentType) {
    var a = document.createElement("a");
    var file = new Blob([content], {type: contentType});
    a.href = URL.createObjectURL(file);
    a.download = fileName;
    a.click();
}

download(JSON.stringify(classObs), filename, 'application/json');