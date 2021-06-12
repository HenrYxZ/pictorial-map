class PPMFile {
  constructor(file) {
    this.file = file;
  }

  init() {
    // Read file as text
    const fileReader = new FileReader();
    await fileReader.readAsText(this.file);
    const fileText = fileReader.result;
    const textLines = fileText.split('\n');
    this.magicNumber = textLines[0];
    const wh = textLines[1].split(' ');
    this.width = parseInt(wh[0]);
    this.height = parseInt(wh[1]);
    this.maxValue = parseInt(textLines[2]);
    this.data = [];
    for (let i = 3; i < textLines.length; i++) {
      let row = [];
      for (let col of textLines[i].split(' ')) {
        row.push(parseInt(col))
      }
      this.data.push(row);
    }
  }
}
