// Copyright (c) Matthias Fischer
// Distributed under the terms of the Modified BSD License.

import {
  DOMWidgetModel,
  DOMWidgetView,
  ISerializers,
} from '@jupyter-widgets/base';

import { MODULE_NAME, MODULE_VERSION } from './version';

// Import the CSS
import '../css/widget.css';

export class CanvasModel extends DOMWidgetModel {
  defaults() {
    return {
      ...super.defaults(),
      _model_name: CanvasModel.model_name,
      _model_module: CanvasModel.model_module,
      _model_module_version: CanvasModel.model_module_version,
      _view_name: CanvasModel.view_name,
      _view_module: CanvasModel.view_module,
      _view_module_version: CanvasModel.view_module_version,
      width: 28,
      height: 28,
      zoom: 8.0,
      base64_data: '',
    };
  }

  static serializers: ISerializers = {
    ...DOMWidgetModel.serializers,
    image_data: { deserialize: (value: DataView) => new Uint8Array(value.buffer) },
  };

  static model_name = 'CanvasModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'CanvasView';
  static view_module = MODULE_NAME;
  static view_module_version = MODULE_VERSION;
}

export class CanvasView extends DOMWidgetView {
  canvas: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;
  isDrawing = false;
  color = '#fff';
  lastPos = { x: 0, y: 0 };
  canvasWrapper: HTMLDivElement;
  
  render() {
    this.el.classList.add('ipypencil-canvas-widget');
    
    // Create a wrapper div for the canvas
    this.canvasWrapper = document.createElement('div');
    this.canvasWrapper.style.position = 'relative';
    this.el.appendChild(this.canvasWrapper);
    
    // Create the canvas
    this.canvas = document.createElement('canvas');
    this.canvas.width = this.model.get('width');
    this.canvas.height = this.model.get('height');
    this.ctx = this.canvas.getContext('2d', { willReadFrequently: true })!;
    
    // Set canvas rendering properties
    this.ctx.imageSmoothingEnabled = false;
    
    // Apply styles for zooming
    this.updateCanvasZoom();
    
    // Add to DOM
    this.canvasWrapper.appendChild(this.canvas);
    
    // Fill with white background
    this.ctx.fillStyle = '#000';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    
    // Add event listeners for drawing
    this.setupEventListeners();
    
    // Listen for changes
    this.model.on('change:width', this.updateCanvasSize, this);
    this.model.on('change:height', this.updateCanvasSize, this);
    this.model.on('change:zoom', this.updateCanvasZoom, this);
    this.model.on('msg:custom', this.onCustomMessage, this);
    
    // Add grid overlay if needed
    this.updateGrid();
    
    // Initialize image data
    this.updateImageData();
  }
  
  updateCanvasSize() {
    // Update actual canvas dimensions
    this.canvas.width = this.model.get('width');
    this.canvas.height = this.model.get('height');
    
    // Clear canvas with white background when size changes
    this.ctx.fillStyle = 'white';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    this.ctx.fillStyle = 'black';
    
    // Update zoom-related styles
    this.updateCanvasZoom();
    
    // Update grid
    this.updateGrid();
    
    // Update image data
    this.updateImageData();
  }
  
  updateCanvasZoom() {
    const zoom = this.model.get('zoom');
    const width = this.model.get('width');
    const height = this.model.get('height');
    
    // Apply CSS transforms to scale the canvas
    this.canvas.style.width = `${width * zoom}px`;
    this.canvas.style.height = `${height * zoom}px`;
    this.canvas.style.imageRendering = 'pixelated'; // Ensure crisp pixel scaling
    
    // Update the wrapper dimensions
    this.canvasWrapper.style.width = `${width * zoom}px`;
    this.canvasWrapper.style.height = `${height * zoom}px`;
    
    // Update grid if needed
    this.updateGrid();
  }
  
  updateGrid() {
    // Remove any existing grid
    const existingGrid = this.canvasWrapper.querySelector('.ipypencil-grid');
    if (existingGrid) {
      this.canvasWrapper.removeChild(existingGrid);
    }
    
    const zoom = this.model.get('zoom');
    
    // Only draw grid if zoom is large enough
    if (zoom >= 4) {
      const gridCanvas = document.createElement('canvas');
      gridCanvas.className = 'ipypencil-grid';
      gridCanvas.width = this.model.get('width') * zoom;
      gridCanvas.height = this.model.get('height') * zoom;
      gridCanvas.style.position = 'absolute';
      gridCanvas.style.top = '0';
      gridCanvas.style.left = '0';
      gridCanvas.style.pointerEvents = 'none'; // Make grid non-interactive
      
      const gridCtx = gridCanvas.getContext('2d')!;
      const width = this.model.get('width');
      const height = this.model.get('height');
      
      gridCtx.strokeStyle = 'rgba(0, 0, 0, 0.1)';
      gridCtx.lineWidth = 1;
      
      // Draw vertical grid lines
      for (let x = 0; x <= width; x++) {
        gridCtx.beginPath();
        gridCtx.moveTo(x * zoom, 0);
        gridCtx.lineTo(x * zoom, height * zoom);
        gridCtx.stroke();
      }
      
      // Draw horizontal grid lines
      for (let y = 0; y <= height; y++) {
        gridCtx.beginPath();
        gridCtx.moveTo(0, y * zoom);
        gridCtx.lineTo(width * zoom, y * zoom);
        gridCtx.stroke();
      }
      
      // Add grid overlay
      this.canvasWrapper.appendChild(gridCanvas);
    }
  }
  
  setupEventListeners() {
    this.canvas.addEventListener('mousedown', this.onMouseDown.bind(this));
    this.canvas.addEventListener('mousemove', this.onMouseMove.bind(this));
    this.canvas.addEventListener('mouseup', this.onMouseUp.bind(this));
    this.canvas.addEventListener('mouseleave', this.onMouseUp.bind(this));
    this.canvas.addEventListener('touchstart', this.onTouchStart.bind(this));
    this.canvas.addEventListener('touchmove', this.onTouchMove.bind(this));
    this.canvas.addEventListener('touchend', this.onTouchEnd.bind(this));
  }
  
  onMouseDown(event: MouseEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDrawing = true;
    this.color = event.button === 1 ? '#000' : '#fff'; // Middle click to erase
    this.lastPos = this.getMousePosition(event);
  }
  
  onMouseMove(event: MouseEvent) {
    if (!this.isDrawing) return;
    const pos = this.getMousePosition(event);
    this.draw(pos.x, pos.y, this.color);
    this.lastPos = pos;
  }
  
  onMouseUp() {
    if (this.isDrawing) {
      this.isDrawing = false;
      this.updateImageData();
    }
  }
  
  onTouchStart(event: TouchEvent) {
    if (event.touches.length === 1) {
      event.preventDefault();
      this.isDrawing = true;
      this.color = '#fff';
      const touch = event.touches[0];
      this.lastPos = this.getTouchPosition(touch);
    }
  }
  
  onTouchMove(event: TouchEvent) {
    if (!this.isDrawing || event.touches.length !== 1) return;
    event.preventDefault();
    const touch = event.touches[0];
    const pos = this.getTouchPosition(touch);
    this.draw(pos.x, pos.y, this.color);
    this.lastPos = pos;
  }
  
  onTouchEnd(event: TouchEvent) {
    this.isDrawing = false;
    this.updateImageData();
  }
  
  getMousePosition(event: MouseEvent) {
    const rect = this.canvas.getBoundingClientRect();
    const scaleX = this.canvas.width / rect.width;
    const scaleY = this.canvas.height / rect.height;
    return {
      x: Math.floor((event.clientX - rect.left) * scaleX),
      y: Math.floor((event.clientY - rect.top) * scaleY)
    };
  }
  
  getTouchPosition(touch: Touch) {
    const rect = this.canvas.getBoundingClientRect();
    const scaleX = this.canvas.width / rect.width;
    const scaleY = this.canvas.height / rect.height;
    return {
      x: Math.floor((touch.clientX - rect.left) * scaleX),
      y: Math.floor((touch.clientY - rect.top) * scaleY)
    };
  }
  
  draw(x: number, y: number, color = '#fff') {
    this.ctx.beginPath();
    this.ctx.lineWidth = 1;
    this.ctx.lineCap = "round";
    this.ctx.strokeStyle = color;

    this.ctx.moveTo(this.lastPos.x, this.lastPos.y);
    this.ctx.lineTo(x, y);
    this.ctx.stroke();
  }
  
  updateImageData() {
    // Get image data from canvas
    const imageData = this.ctx.getImageData(
      0, 0, this.canvas.width, this.canvas.height
    );

    const grayscaleValues = [];

    // Helligkeitswerte für jeden Pixel berechnen
    for (let i = 0; i < imageData.data.length; i += 4) {
      const r = imageData.data[i];
      const g = imageData.data[i + 1];
      const b = imageData.data[i + 2];
      const grayscale = Math.round(0.299 * r + 0.587 * g + 0.114 * b); // Graustufenwert berechnen
      grayscaleValues.push(grayscale);
    }
    
    const buffer = new ArrayBuffer(grayscaleValues.length);
    const uint8Array = new Uint8Array(buffer);
    uint8Array.set(grayscaleValues);
    
    const base64String = btoa(String.fromCharCode(...uint8Array));
    
    // Update model
    this.model.set('base64_data', base64String, { updated_view: this });

    this.model.save_changes();
  }
  
  onCustomMessage(msg: any) {
    if (msg.action === 'clear') {
      this.clear();
    } else if (msg.action === 'update_image_data') {
      this.updateImageData();
    }
  }
  
  clear() {
    // Clear canvas with white background
    this.ctx.fillStyle = '#000';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    
    // Update image data
    this.updateImageData();
  }
}