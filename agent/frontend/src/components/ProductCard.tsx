import { Card } from "./ui/card";
import { ImageWithFallback } from "./figma/ImageWithFallback";

interface ProductCardProps {
  image: string;
  title: string;
  price: string;
}

export function ProductCard({ image, title, price }: ProductCardProps) {
  return (
    <div className="group cursor-pointer transition-all duration-300 ease-out hover:-translate-y-0.5">
      <Card className="overflow-hidden border-0 bg-white rounded-[20px] transition-all duration-300">
        <div className="aspect-[4/3] relative overflow-hidden bg-white">
          <ImageWithFallback
            src={image}
            alt={title}
            className="w-full h-full object-cover transition-transform duration-500 ease-out group-hover:scale-[1.02]"
          />
        </div>
        <div className="px-4 py-3 bg-white space-y-1">
          <h3 className="text-gray-900 text-[14px] font-[600] leading-tight tracking-[-0.01em]">
            {title}
          </h3>
          <p className="text-gray-700 text-[13px] font-[500]">
            {price}
          </p>
        </div>
      </Card>
    </div>
  );
}
