import { 
    Connection, 
    PublicKey, 
    Transaction, 
    SystemProgram,
    clusterApiUrl,
    sendAndConfirmTransaction
} from '@solana/web3.js';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

// Funkcja do pobrania danych sprzedawcy z backendu
const getSellerPublicKey = async (seller_id) => {
    try {
        const response = await fetch(`${BACKEND_URL}/sellers/${seller_id}`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        });

        if (!response.ok) 
        {
            throw new Error(`Failed to fetch seller data: ${response.status}`);
        }

        const seller = await response.json();
        return seller.public_key; // Zwraca klucz publiczny sprzedawcy
    } 
    catch (err) 
    {
        console.error("Error fetching seller data:", err);
        throw new Error("Unable to fetch seller data.");
    }
};

// Funkcja do pobrania produktów użytkownika z backendu
const getUserProducts = async (user_id) => {
    try {
        const response = await fetch(`${BACKEND_URL}/users/${user_id}/products`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        });

        if (!response.ok) 
        {
            throw new Error(`Failed to fetch user products: ${response.status}`);
        }

        const products = await response.json();
        return products; // Zwraca tablicę produktów użytkownika
    } 
    catch (err) 
    {
        console.error("Error fetching user products:", err);
        throw new Error("Unable to fetch user products.");
    }
};

const handlePurchaseWithFee = async (amount, seller_id, user_id, product_id) => {
    try {
        // Check if Phantom Wallet is installed
        if (!window.solana || !window.solana.isPhantom) 
        {
            alert("Please install Phantom Wallet!");
            return;
        }
        
        // Connect to Phantom Wallet if not already connected
        if (!window.solana.isConnected) 
        {
            await window.solana.connect();
        }

        // Pobierz klucz publiczny sprzedawcy z backendu
        const sellerPublicKeyString = await getSellerPublicKey(seller_id);
        const sellerPublicKey = new PublicKey(sellerPublicKeyString);
        const neuroSpherePublicKey = new PublicKey(process.env.NEXT_PUBLIC_NEUROSPHERE_PUBLIC_KEY);

        // Pobierz produkty użytkownika z backendu
        const userProducts = await getUserProducts(user_id);
        console.log("User products:", userProducts);

        // Sprawdź, czy użytkownik już kupił ten produkt
        if (userProducts.some(product => product.id === product_id)) 
        {
            alert("You have already purchased this product.");
            return;
        }

        const connection = new Connection(clusterApiUrl('devnet'), 'confirmed');
        
        const totalLamports = amount * 1_000_000_000;
        
        const feeLamports = Math.floor(totalLamports * 0.1); // 10% for NeuroSphere
        const sellerLamports = totalLamports - feeLamports; // 90% for the seller
        
        const transaction = new Transaction();
        
        transaction.add(
            SystemProgram.transfer({
                fromPubkey: window.solana.publicKey,
                toPubkey: sellerPublicKey,
                lamports: sellerLamports,
            })
        );
        
        transaction.add(
            SystemProgram.transfer({
                fromPubkey: window.solana.publicKey,
                toPubkey: neuroSpherePublicKey,
                lamports: feeLamports,
            })
        );
        
        transaction.feePayer = window.solana.publicKey;
        
        const blockhash = await connection.getLatestBlockhash();
        transaction.recentBlockhash = blockhash.blockhash;
        
        // Ask the user to sign the transaction
        const signedTransaction = await window.solana.signTransaction(transaction);
        
        // Send the signed transaction to SOL
        const signature = await connection.sendRawTransaction(signedTransaction.serialize());
        
        console.log('Transaction sent:', signature);
        
        // Confirm the transaction
        const confirmation = await connection.confirmTransaction(signature, 'confirmed');
        
        if (confirmation.value.err) 
        {
            alert('Transaction confirmation failed');
            return;
        }
        
        console.log('Transaction confirmed:', signature);
        console.log(`Sent ${sellerLamports/1_000_000_000} SOL to seller and ${feeLamports/1_000_000_000} SOL to NeuroSphere`);
        alert(`Payment successfully completed! Transaction ID: ${signature}`);
        
        // Send transaction details to backend
        try {
            const updateResponse = await fetch(`${BACKEND_URL}/users/${user_id}/products`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    product_id: product_id,
                    transaction_id: signature,
                }),
            });

            if (!updateResponse.ok) 
            {
                throw new Error(`Failed to update user products: ${updateResponse.status}`);
            }

            const updateResult = await updateResponse.json();
            console.log("Product successfully added to user:", updateResult);

        } 
        catch (backendErr) 
        {
            console.error('Error updating user products in backend:', backendErr);
        }
    } 
    catch (err) 
    {
        console.error('Error during purchase with fee:', err);
        alert(`An error occurred: ${err.message}`);
    }
};

export default handlePurchaseWithFee;
