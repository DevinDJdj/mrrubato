class SignTool {
    constructor() {
      this.initVars()
      this.initEvents()
    }
  
    initVars() {
      this.canvas = $('#capturescreen')[0]
      this.ctx = this.canvas.getContext("2d")
      this.strokeColor = editcolor
      this.isMouseClicked = false
      this.isMouseInCanvas = false
      this.prevX = 0
      this.currX = 0
      this.prevY = 0
      this.currY = 0
    }
  
    initEvents() {
      $('#capturescreen').on("mousemove", (e) => this.onMouseMove(e))
      $('#capturescreen').on("mousedown", (e) => this.onMouseDown(e))
      $('#capturescreen').on("mouseup", (e) => this.onMouseUp(e))
      $('#capturescreen').on("mouseout", () => this.onMouseOut())
      $('#capturescreen').on("mouseenter", (e) => this.onMouseEnter(e))
    }
    
    onMouseDown(e) {
        this.isMouseClicked = true
      this.updateCurrentPosition(e)

    }
    
    onMouseUp(e) {
        this.isMouseClicked = false
        if (drawFunction == 1){
          this.updateCurrentPosition(e);
          this.draw();
        }
    }
    
    onMouseEnter(e) {
        this.isMouseInCanvas = true
        if (drawFunction == 0){
          this.updateCurrentPosition(e)
        }
    }
    
    onMouseOut() {
        this.isMouseInCanvas = false
    }
  
    onMouseMove(e) {
      if (this.isMouseClicked && this.isMouseInCanvas && drawFunction == 0) {
          this.updateCurrentPosition(e)
        this.draw()
      }
    }
    
    updateCurrentPosition(e) {
        this.prevX = this.currX
        this.prevY = this.currY
        this.currX = e.clientX - this.canvas.offsetLeft
        this.currY = e.clientY - this.canvas.offsetTop
    }
    
    draw() {
      if (drawFunction ==0){
        this.ctx.beginPath()
        this.ctx.moveTo(this.prevX, this.prevY)
        this.ctx.lineTo(this.currX, this.currY)
        this.ctx.strokeStyle = this.strokeColor
        this.ctx.lineWidth = 10
        this.ctx.stroke()
        this.ctx.closePath()
      }
      else if (drawFunction==1){
        this.ctx.beginPath()
        this.ctx.strokeStyle = this.strokeColor
        this.ctx.rect(this.prevX, this.prevY, this.currX-this.prevX, this.currY-this.prevY)
        this.ctx.stroke()
      }
      else{
        this.ctx.font = '20px Arial';
        this.ctx.fillStyle = this.strokeColor

        // Set the global alpha value (0.0 - 1.0)
        this.ctx.globalAlpha = 0.5;

        this.ctx.fillText(drawText, this.currX, this.currY);

      }
    }
  }
  
