function support_popup(option, height, width, inner_html) {
  option['toolbox']['feature']['myFeature'] = {
    show: true,
    title: 'Open in new window',
    icon: "image://data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iNDhweCIgd2lkdGg9IjQ4cHgiIHZpZXdCb3g9IjE2MCAtODAwIDY0MCA2NDAiIGZpbGw9IiM2NjY2NjYiPg0KICA8cGF0aCBkPSJNMjE1LjM4LTE2MHEtMjMuMDUgMC0zOS4yMi0xNi4xNlExNjAtMTkyLjMzIDE2MC0yMTUuMzh2LTUyOS4yNHEwLTIzLjA1IDE2LjE2LTM5LjIyUTE5Mi4zMy04MDAgMjE1LjM4LTgwMGgyMjQuMzl2MzAuNzdIMjE1LjM4cS05LjIzIDAtMTYuOTIgNy42OS03LjY5IDcuNjktNy42OSAxNi45MnY1MjkuMjRxMCA5LjIzIDcuNjkgMTYuOTIgNy42OSA3LjY5IDE2LjkyIDcuNjloNTI5LjI0cTkuMjMgMCAxNi45Mi03LjY5IDcuNjktNy42OSA3LjY5LTE2Ljkydi0yMjQuMzlIODAwdjIyNC4zOXEwIDIzLjA1LTE2LjE2IDM5LjIyUTc2Ny42Ny0xNjAgNzQ0LjYyLTE2MEgyMTUuMzhabTE3MS4yNC0yMDQuMzgtMjItMjIuMjQgMzgyLjYxLTM4Mi42MUg1NDEuMzFWLTgwMEg4MDB2MjU4LjY5aC0zMC43N1YtNzQ3TDM4Ni42Mi0zNjQuMzhaIi8+DQo8L3N2Zz4NCg==",
    onclick: function (){
      var height_ = Math.min(screen.height, Math.round(1.5 * parseInt(height.slice(0,-2))))
      var width_ = Math.min(screen.width, Math.round(1.5 * parseInt(width.slice(0,-2))))
      var left = (screen.width/2)-(width_/2);
      var top = (screen.height/2)-(height_/2);
      var win = window.open('template.html', '_blank',
        `height=${height_}px, width=${width_}px, top=${top}px, left=${left}px`,
      );
      win.document.write(`${inner_html}`);
      win.document.close();
    }
  };
  return option;
};