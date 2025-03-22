// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

// Add any needed widget imports here (or from controls)
// import {} from '@jupyter-widgets/base';

import { createTestModel } from './utils';

import { CanvasModel } from '..';

describe('Canvas', () => {
  describe('CanvasModel', () => {
    it('should be createable with default values', () => {
      const model = createTestModel(CanvasModel);
      expect(model).toBeInstanceOf(CanvasModel);
      expect(model.get('width')).toBe(28);
      expect(model.get('height')).toBe(28);
      expect(model.get('zoom')).toBe(8.0);
      expect(model.get('image_data')).toBeInstanceOf(Uint8Array);
      expect(model.get('image_data').length).toBe(0);
    });

    it('should be createable with custom values', () => {
      const state = {
        width: 64,
        height: 48,
        zoom: 4.0,
      };
      const model = createTestModel(CanvasModel, state);
      expect(model).toBeInstanceOf(CanvasModel);
      expect(model.get('width')).toBe(64);
      expect(model.get('height')).toBe(48);
      expect(model.get('zoom')).toBe(4.0);
    });

    it('should update properly when attributes change', () => {
      const model = createTestModel(CanvasModel);
      
      // Set new values
      model.set('width', 100);
      model.set('height', 75);
      model.set('zoom', 2.0);
      
      // Check values were updated
      expect(model.get('width')).toBe(100);
      expect(model.get('height')).toBe(75);
      expect(model.get('zoom')).toBe(2.0);
    });

    it('should have proper serializers', () => {
      // Test that the image_data serializer is present
      expect(CanvasModel.serializers).toBeDefined();
      expect(CanvasModel.serializers.image_data).toBeDefined();
      
      // Create a model with dummy image data
      const testBytes = new Uint8Array([255, 0, 0, 255, 0, 255, 0, 255]);
      const model = createTestModel(CanvasModel, {
        image_data: testBytes
      });
      
      // Verify the image_data was properly set
      const imageData = model.get('image_data');
      expect(imageData).toBeInstanceOf(Uint8Array);
      expect(imageData.length).toBe(8);
      expect(imageData[0]).toBe(255);
      expect(imageData[1]).toBe(0);
    });

    it('should have correct static properties', () => {
      expect(CanvasModel.model_name).toBe('CanvasModel');
      expect(CanvasModel.view_name).toBe('CanvasView');
    });
  });
});
