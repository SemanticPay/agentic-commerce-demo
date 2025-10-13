import React from 'react'
import { ProductWidgetData } from '../types'

interface ProductWidgetProps {
  data: ProductWidgetData
}

const ProductWidget: React.FC<ProductWidgetProps> = ({ data }) => {
  const formatPrice = (price: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(price)
  }

  return (
    <div className="product-widget">
      <div className="product-image-container">
        <img 
          src={data.image_url} 
          alt={data.title}
          className="product-image"
        />
      </div>
      <div className="product-details">
        <h3 className="product-title">{data.title}</h3>
        {data.description && (
          <p className="product-description">{data.description}</p>
        )}
        <p className="product-price">
          {formatPrice(data.price, data.currency)}
        </p>
      </div>
    </div>
  )
}

export default ProductWidget
