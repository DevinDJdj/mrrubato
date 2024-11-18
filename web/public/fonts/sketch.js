// only works with opentype fonts

let font;


function modifyPath(p) {
  let newCommands = [];
  for (let cmd of p.commands) {    
    let newC = Object.assign({}, cmd);
    if (newC.hasOwnProperty('x')) {
      newC.x += (Math.random()-0.5)*50;
      newC.y += (Math.random()-0.5)*50;
    }
    //console.log(cmd, newC);
    newCommands.push(newC);
  }
  let newPath = new opentype.Path();
  newPath.extend(newCommands);
  return newPath;
} 

let path;

function setup(f, drawingContext) {

  font = f;
  font.draw(drawingContext, "abcdefgABCDEFG", 0, 100, 48);
  
  console.log("modifying glyphs");
  for (let i = 0; i < font.glyphs.length; i++) {
  //for (let i = 0; i < 100; i++) {
    let glyph = font.glyphs.glyphs[i];
    glyph.path = modifyPath(glyph.path);
    // this is needed by getPath but is usually set when loading from a file...
    glyph.path.unitsPerEm = font.unitsPerEm;
    //console.log("glyph.path", glyph.path, glyph.path.commands, glyph.path.unitsPerEm);
    //console.log("getpath", glyph.getPath(0, 0, 72, {hinting: false}, font));
  }
  console.log("done");
  // set this to what you want the name of the font to be...
  font.names.fontFamily.en = 'Messed up font nice';
  font.draw(drawingContext, "abcdefgABCDEFG", 0, 200, 48);
//  font.download();
  

}

