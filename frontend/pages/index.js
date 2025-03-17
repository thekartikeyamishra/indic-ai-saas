import { useState } from "react";
import axios from "axios";
import { signIn, signOut, useSession } from "next-auth/react";


export default function Home() {
    
  const [inputText, setInputText] = useState("");
  const [outputText, setOutputText] = useState("");
  const { data: session } = useSession();


  const handlePayment = async () => {
    const response = await axios.post("http://127.0.0.1:8000/create_order", {
      amount: 999,  // ₹999/month
      email: "user@example.com"
    });
  
    const { order_id } = response.data;
  
    const options = {
      key: "your_razorpay_key",
      amount: 99900,
      currency: "INR",
      name: "Indic AI Writer",
      description: "AI Content Generator Subscription",
      order_id: order_id,
      handler: function (response) {
        alert("Payment Successful: " + response.razorpay_payment_id);
      }
    };
  
    const rzp = new window.Razorpay(options);
    rzp.open();
  };
  
  const generateText = async () => {
    const response = await axios.post("http://127.0.0.1:8000/generate", { input_text: inputText });
    setOutputText(response.data.generated_text);
  };

  const sendWhatsApp = async () => {
    const phone = prompt("Enter your WhatsApp Number (with country code):");
    const message = prompt("Enter your message:");
  
    await axios.post("http://127.0.0.1:8000/send_whatsapp", {
      phone,
      message
    });
  
    alert("Message sent to WhatsApp!");
  };
  

  return (
    <div className="p-6 text-center">
      {session ? (
        <>
          <h2>Welcome, {session.user.name}!</h2>
          <button onClick={() => signOut()} className="bg-red-500 text-white px-4 py-2">
            Logout
          </button>
        </>
      ) : (
        <>
          <button onClick={() => signIn("google")} className="bg-blue-500 text-white px-4 py-2">
            Sign in with Google
          </button>
        </>
      )}

    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <h1 className="text-3xl font-bold">Indic AI Writer</h1>
      <textarea
        className="mt-4 p-2 w-2/3 border border-gray-300"
        placeholder="Enter text in Hindi, Tamil, etc."
        value={inputText}
        onChange={(e) => setInputText(e.target.value)}
      />
      <button onClick={generateText} className="mt-4 bg-blue-500 text-white px-4 py-2 rounded">
        Generate
      </button>
      {outputText && (
        <div className="mt-4 p-4 bg-white shadow-md">{outputText}</div>
      )}
      </div>
    </div>
  );
}
