import { useState } from "react";
import axios from "axios";

export default function Billing() {
  const [amount, setAmount] = useState(10);

  const handlePayment = async () => {
    const response = await axios.post("http://127.0.0.1:8000/purchase_credits", {
      email: "user@example.com",
      amount
    });

    window.open(response.data.client_secret, "_blank");
  };

  return (
    <div className="p-6 text-center">
      <h2>Buy Credits</h2>
      <input type="number" value={amount} onChange={(e) => setAmount(e.target.value)} className="border p-2"/>
      <button onClick={handlePayment} className="bg-green-500 text-white px-4 py-2 mt-2">
        Pay ₹{amount * 10}
      </button>
    </div>
  );
}
