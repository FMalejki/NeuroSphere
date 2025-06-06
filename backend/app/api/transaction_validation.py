"""
Connection with Solana
"""
from fastapi import APIRouter, HTTPException

router = APIRouter()

# Solana RPC endpoint (symulacja)
SOLANA_RPC_URL = "https://api.devnet.solana.com"

@router.post("/validate-transaction")
async def validate_transaction(transaction_id: str, seller_public_key: str, neurosphere_public_key: str, seller_amount: int, fee_amount: int):
    try:
        transaction_details = {
            "result": {
                "meta": {
                    "preBalances": [1000000000, 2000000000, 3000000000],
                    "postBalances": [900000000, 2100000000, 3100000000],
                },
                "transaction": {
                    "message": {
                        "accountKeys": [
                            "buyer_public_key",
                            seller_public_key,
                            neurosphere_public_key  
                        ]
                    }
                }
            }
        }

        # Analiza szczegółów transakcji
        result = transaction_details.get("result")
        if not result:
            raise HTTPException(status_code=404, detail="Transaction not found on blockchain")

        meta = result.get("meta")
        if not meta or meta.get("err"):
            raise HTTPException(status_code=400, detail="Transaction failed or invalid")

        # Sprawdzenie transferów
        pre_balances = meta.get("preBalances", [])
        post_balances = meta.get("postBalances", [])
        account_keys = result["transaction"]["message"]["accountKeys"]

        # Sprawdzenie sald sprzedawcy i NeuroSphere
        try:
            seller_index = account_keys.index(seller_public_key)
            neurosphere_index = account_keys.index(neurosphere_public_key)
        except ValueError:
            raise HTTPException(status_code=400, detail="Public keys not found in transaction")

        seller_balance_diff = post_balances[seller_index] - pre_balances[seller_index]
        neurosphere_balance_diff = post_balances[neurosphere_index] - pre_balances[neurosphere_index]

        if seller_balance_diff != seller_amount or neurosphere_balance_diff != fee_amount:
            pass

        return {"status": "success", "message": "Transaction validated successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating transaction: {str(e)}")


# # Definicja modeli danych
# class TransactionData(BaseModel):
#     transaction_id: str
#     buyer_public_key: str
#     seller_public_key: str
#     neurosphere_public_key: str
#     total_amount: int
#     seller_amount: int
#     fee_amount: int

# class ValidationDetails(BaseModel):
#     is_fee_correct: bool
#     is_seller_amount_correct: bool
#     found_seller_transfer: bool
#     found_neurosphere_transfer: bool

# class ValidationResponse(BaseModel):
#     status: str
#     message: str
#     details: Optional[ValidationDetails] = None

# # Inicjalizacja routera FastAPI
# router = APIRouter()

# # Funkcja pomocnicza do inicjalizacji klienta Solana
# def init_solana_client():
#     return Client("https://api.devnet.solana.com")

# # Endpoint do walidacji transakcji
# @router.post("/validate-transaction", response_model=ValidationResponse)
# async def validate_transaction(transaction_data: TransactionData):
#     # Inicjalizacja klienta Solana
#     client = init_solana_client()
    
#     try:
#         # Parsowanie kluczy publicznych
#         try:
#             buyer_pubkey = PublicKey(transaction_data.buyer_public_key)
#             seller_pubkey = PublicKey(transaction_data.seller_public_key)
#             neurosphere_pubkey = PublicKey(transaction_data.neurosphere_public_key)
#         except Exception as e:
#             raise HTTPException(
#                 status_code=400, 
#                 detail=ValidationResponse(
#                     status="error",
#                     message=f"Invalid public key: {str(e)}",
#                     details=None
#                 ).model_dump()
#             )
        
#         # Pobranie szczegółów transakcji
#         try:
#             tx_response = client.get_transaction(
#                 tx_sig=transaction_data.transaction_id,
#                 encoding="base64"
#             )
#         except Exception as e:
#             raise HTTPException(
#                 status_code=500, 
#                 detail=ValidationResponse(
#                     status="error",
#                     message=f"Error retrieving transaction: {str(e)}",
#                     details=None
#                 ).model_dump()
#             )
        
#         # Sprawdzanie czy transakcja zawiera metadane
#         if not tx_response.get("result"):
#             raise HTTPException(
#                 status_code=400, 
#                 detail=ValidationResponse(
#                     status="failure",
#                     message="Invalid transaction or transaction not found",
#                     details=None
#                 ).model_dump()
#             )
            
#         result = tx_response["result"]
#         meta = result.get("meta")
        
#         if not meta:
#             raise HTTPException(
#                 status_code=400, 
#                 detail=ValidationResponse(
#                     status="failure",
#                     message="Transaction metadata missing",
#                     details=None
#                 ).model_dump()
#             )
        
#         # Sprawdzenie czy transakcja zakończyła się sukcesem
#         if meta.get("err"):
#             raise HTTPException(
#                 status_code=400, 
#                 detail=ValidationResponse(
#                     status="failure",
#                     message=f"Transaction failed: {meta['err']}",
#                     details=None
#                 ).model_dump()
#             )
            
#         # Inicjalizacja flag walidacji
#         found_seller_transfer = False
#         found_neurosphere_transfer = False
#         seller_transfer_amount = 0
#         neurosphere_transfer_amount = 0
        
#         # Metoda 1: Sprawdzenie różnic w saldach przed i po transakcji
#         pre_balances = meta.get("preBalances", [])
#         post_balances = meta.get("postBalances", [])
        
#         transaction = result.get("transaction")
#         if not transaction:
#             raise HTTPException(
#                 status_code=400, 
#                 detail=ValidationResponse(
#                     status="failure",
#                     message="Transaction data missing",
#                     details=None
#                 ).model_dump()
#             )
            
#         # Dekodowanie i analiza transakcji
#         if "message" in transaction:
#             message = transaction["message"]
#             account_keys = message.get("accountKeys", [])
            
#             # Mapowanie kluczy kont na indeksy
#             account_indices = {}
#             for i, key in enumerate(account_keys):
#                 account_indices[key] = i
                
#             # Sprawdzenie sald dla sprzedawcy i NeuroSphere
#             seller_pubkey_str = str(seller_pubkey)
#             neurosphere_pubkey_str = str(neurosphere_pubkey)
            
#             if seller_pubkey_str in account_indices and account_indices[seller_pubkey_str] < len(pre_balances) and account_indices[seller_pubkey_str] < len(post_balances):
#                 seller_idx = account_indices[seller_pubkey_str]
#                 balance_diff = post_balances[seller_idx] - pre_balances[seller_idx]
#                 if balance_diff > 0:
#                     found_seller_transfer = True
#                     seller_transfer_amount = balance_diff
                    
#             if neurosphere_pubkey_str in account_indices and account_indices[neurosphere_pubkey_str] < len(pre_balances) and account_indices[neurosphere_pubkey_str] < len(post_balances):
#                 neurosphere_idx = account_indices[neurosphere_pubkey_str]
#                 balance_diff = post_balances[neurosphere_idx] - pre_balances[neurosphere_idx]
#                 if balance_diff > 0:
#                     found_neurosphere_transfer = True
#                     neurosphere_transfer_amount = balance_diff
                    
#         # Metoda 2: Sprawdzenie transferów tokenów (dla SPL Token)
#         if not (found_seller_transfer and found_neurosphere_transfer):
#             token_balances = meta.get("postTokenBalances", [])
#             pre_token_balances = meta.get("preTokenBalances", [])
            
#             # Obliczenie różnic w saldach tokenów
#             token_diffs = {}
            
#             # Inicjalizacja słownika różnic z wartościami początkowymi 0
#             for balance in pre_token_balances + token_balances:
#                 account_index = balance["accountIndex"]
#                 if account_index not in token_diffs:
#                     token_diffs[account_index] = 0
            
#             # Odejmowanie sald przed transakcją
#             for balance in pre_token_balances:
#                 account_index = balance["accountIndex"]
#                 amount = int(balance["uiTokenAmount"]["amount"])
#                 token_diffs[account_index] -= amount
            
#             # Dodawanie sald po transakcji
#             for balance in token_balances:
#                 account_index = balance["accountIndex"]
#                 amount = int(balance["uiTokenAmount"]["amount"])
#                 token_diffs[account_index] += amount
                
#                 # Sprawdzenie czy to saldo sprzedawcy lub NeuroSphere
#                 if "owner" in balance and balance["owner"] == seller_pubkey_str and token_diffs[account_index] > 0:
#                     found_seller_transfer = True
#                     seller_transfer_amount = token_diffs[account_index]
                
#                 if "owner" in balance and balance["owner"] == neurosphere_pubkey_str and token_diffs[account_index] > 0:
#                     found_neurosphere_transfer = True
#                     neurosphere_transfer_amount = token_diffs[account_index]
        
#         # Metoda 3: Analiza instrukcji systemowych dla natywnych transferów SOL
#         if not (found_seller_transfer and found_neurosphere_transfer):
#             # Sprawdzenie instrukcji w transakcji dla natywnych transferów SOL
#             if "instructions" in message:
#                 instructions = message["instructions"]
#                 for instruction in instructions:
#                     # Sprawdzenie czy to instrukcja systemu Solana
#                     program_id_idx = instruction.get("programIdIndex")
#                     if program_id_idx is not None and program_id_idx < len(account_keys):
#                         program_id = account_keys[program_id_idx]
#                         if program_id == str(SYS_PROGRAM_ID):
#                             # Sprawdzenie czy to instrukcja transferu
#                             if "data" in instruction:
#                                 # Dekodowanie danych instrukcji
#                                 try:
#                                     data = base64.b64decode(instruction["data"])
#                                     # Instrukcja transferu ma identyfikator 2 w pierwsych 4 bajtach
#                                     if len(data) >= 4 and int.from_bytes(data[:4], byteorder='little') == 2:
#                                         # Transfer ma format: [4 bajty ID, 8 bajtów kwoty]
#                                         if len(data) >= 12:
#                                             amount = int.from_bytes(data[4:12], byteorder='little')
                                            
#                                             # Sprawdzenie odbiorcy
#                                             if "accounts" in instruction and len(instruction["accounts"]) >= 2:
#                                                 to_idx = instruction["accounts"][1]
#                                                 if to_idx < len(account_keys):
#                                                     to_key = account_keys[to_idx]
                                                    
#                                                     if to_key == seller_pubkey_str:
#                                                         found_seller_transfer = True
#                                                         seller_transfer_amount = amount
#                                                     elif to_key == neurosphere_pubkey_str:
#                                                         found_neurosphere_transfer = True
#                                                         neurosphere_transfer_amount = amount
#                                 except Exception as e:
#                                     # Wyjątek podczas dekodowania - kontynuuj
#                                     pass
        
#         # Walidacja obliczeń opłat
#         is_fee_correct = neurosphere_transfer_amount == transaction_data.fee_amount
#         is_seller_amount_correct = seller_transfer_amount == transaction_data.seller_amount
        
#         # Sprawdzenie czy oba transfery zostały znalezione i czy kwoty są zgodne
#         validation_successful = (found_seller_transfer and found_neurosphere_transfer and 
#                               is_fee_correct and is_seller_amount_correct)
        
#         # Tworzenie szczegółów walidacji
#         details = ValidationDetails(
#             is_fee_correct=is_fee_correct,
#             is_seller_amount_correct=is_seller_amount_correct,
#             found_seller_transfer=found_seller_transfer,
#             found_neurosphere_transfer=found_neurosphere_transfer
#         )
        
#         if validation_successful:
#             return ValidationResponse(
#                 status="success",
#                 message="Transaction validated successfully.",
#                 details=details
#             )
#         else:
#             return ValidationResponse(
#                 status="failure",
#                 message="Transaction validation failed.",
#                 details=details
#             )
            
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=500, 
#             detail=ValidationResponse(
#                 status="error",
#                 message=f"Unexpected error: {str(e)}",
#                 details=None
#             ).model_dump()
#         )
