import { HashRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./components/HomePage";
import ChatPage from "./components/ChatPage";
import CatalogPage from "./components/CatalogPage";
import CartPage from "./components/CartPage";
import ProductPage from "./components/ProductPage";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/catalog" element={<CatalogPage />} />
        <Route path="/cart" element={<CartPage />} />
        <Route path="/product/:id" element={<ProductPage />} />
      </Routes>
    </Router>
  );
}
