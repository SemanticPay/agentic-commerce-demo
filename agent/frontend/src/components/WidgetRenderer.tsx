import React from 'react'
import { Widget, WidgetType } from '../types'

interface WidgetRendererProps {
  widget: Widget
}

const WidgetRenderer: React.FC<WidgetRendererProps> = ({ widget }) => {
  switch (widget.type) {
    case WidgetType.PRODUCT:
      return <div className="product-widget" dangerouslySetInnerHTML={{ __html: widget.raw_html_string }} />
    case WidgetType.CART:
      return <div className="cart-widget" dangerouslySetInnerHTML={{ __html: widget.raw_html_string }} />
    default:
      console.warn('Unknown widget type:', widget.type)
      return null
  }
}

export default WidgetRenderer
