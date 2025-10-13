import React from 'react'
import { Widget, WidgetType, ProductWidgetData, CartWidgetData } from '../types'
import ProductWidget from './ProductWidget'
import CartWidget from './CartWidget'

interface WidgetRendererProps {
  widget: Widget
}

const WidgetRenderer: React.FC<WidgetRendererProps> = ({ widget }) => {
  switch (widget.type) {
    case WidgetType.PRODUCT:
      return <ProductWidget data={widget.data as ProductWidgetData} />
    case WidgetType.CART:
      return <CartWidget data={widget.data as CartWidgetData} />
    default:
      console.warn('Unknown widget type:', widget.type)
      return null
  }
}

export default WidgetRenderer
