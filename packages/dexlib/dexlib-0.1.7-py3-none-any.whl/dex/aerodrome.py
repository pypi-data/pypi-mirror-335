"""
Aerodrome DEX implementation.
"""

import asyncio
import logging
from web3 import Web3
from typing import List, Dict, Any, Tuple, Optional
from eth_typing import ChecksumAddress

from .base import BaseDEX
from .config import (
    AERODROME_ROUTER_ADDRESS,
    AERODROME_FACTORY_ADDRESS,
    AERODROME_ROUTER_ABI,
    AERODROME_FACTORY_ABI,
    ERC20_ABI
)

logger = logging.getLogger(__name__)


class Route:
    """Represents a route for Aerodrome swaps"""
    def __init__(self, from_token: str, to_token: str, stable: bool, factory: str):
        self.from_token = Web3.to_checksum_address(from_token)
        self.to_token = Web3.to_checksum_address(to_token)
        self.stable = stable
        self.factory = Web3.to_checksum_address(factory)

    def to_tuple(self) -> Tuple[ChecksumAddress, ChecksumAddress, bool, ChecksumAddress]:
        """Convert to tuple format expected by the contract"""
        return (self.from_token, self.to_token, self.stable, self.factory)


class AerodromeDEX(BaseDEX):
    """Aerodrome DEX implementation"""

    @property
    def router_address(self) -> str:
        """Get the router address for this DEX"""
        return self._router_address

    def __init__(self, w3: Web3, private_key: str):
        """Initialize Aerodrome DEX"""
        super().__init__(w3, private_key)
        self.token_abi = ERC20_ABI
        self._router_address = AERODROME_ROUTER_ADDRESS
        self.factory_address = AERODROME_FACTORY_ADDRESS
        self.router = self.w3.eth.contract(
            address=self._router_address,
            abi=AERODROME_ROUTER_ABI
        )
        self.factory = self.w3.eth.contract(
            address=self.factory_address,
            abi=AERODROME_FACTORY_ABI
        )
        self.slippage = 0.01  # 1% slippage tolerance

    def get_pool_exists(self, token_a: str, token_b: str, stable: bool) -> bool:
        """Check if pool exists"""
        try:
            pool = self.factory.functions.getPool(
                Web3.to_checksum_address(token_a),
                Web3.to_checksum_address(token_b),
                stable
            ).call()
            logger.info(f"Pool address for {token_a} -> {token_b} (stable={stable}): {pool}")
            return pool != '0x0000000000000000000000000000000000000000'
        except Exception as e:
            error_result = self._handle_error(e, "checking pool existence")
            return False

    def get_quote(self, token_in: str, token_out: str, amount_in: int) -> int:
        """Get quote for a swap"""
        try:
            # First try direct path
            direct_quote = self._try_path([token_in, token_out], amount_in)
            if direct_quote > 0:
                logger.info(f"Direct quote found: {direct_quote}")
                return direct_quote

            raise Exception("No valid quotes found")

        except Exception as e:
            return self._handle_error(e, "getting quote")

    def _try_path(self, path: List[str], amount_in: int) -> int:
        """Try to get a quote for a specific path"""
        try:
            routes = []
            for i in range(len(path) - 1):
                token_in = path[i]
                token_out = path[i + 1]

                # Try both stable and volatile pools
                stable_pool_exists = self.get_pool_exists(token_in, token_out, True)
                volatile_pool_exists = self.get_pool_exists(token_in, token_out, False)

                logger.info(f"Pool check {token_in} -> {token_out}: stable={stable_pool_exists}, volatile={volatile_pool_exists}")

                # Try both stable and volatile pools
                if stable_pool_exists:
                    routes.append(Route(token_in, token_out, True, self.factory_address))
                if volatile_pool_exists:
                    routes.append(Route(token_in, token_out, False, self.factory_address))
                if not (stable_pool_exists or volatile_pool_exists):
                    return 0  # No valid pool for this pair

            if not routes:
                return 0

            # Convert routes to tuples
            routes = [r.to_tuple() for r in routes]

            try:
                quote = self.router.functions.getAmountsOut(
                    amount_in,
                    routes
                ).call()
                logger.info(f"Quote for path {path}: {quote}")
                return quote[-1]  # Return the final output amount
            except Exception as e:
                logger.error(f"Error getting quote for path {path}: {str(e)}")
                return 0

        except Exception as e:
            error_result = self._handle_error(e, f"trying path {path}")
            return 0

    def swap_tokens(self, token_in: str, token_out: str, amount_in: int) -> Optional[Dict[str, Any]]:
        """Swap tokens using Aerodrome router"""
        try:
            # Wait for any pending transactions first
            self._wait_for_pending_txs(token_in, token_out)
            logger.info(f"Starting swap of {amount_in} {token_in} to {token_out}")
            
            # Check balance first
            token = self.w3.eth.contract(address=Web3.to_checksum_address(token_in), abi=self.token_abi)
            block = self.w3.eth.block_number
            balance = token.functions.balanceOf(self.address).call(block_identifier=block)
            if balance < amount_in:
                return {'success': False, 'error': f'Insufficient balance: have {balance}, need {amount_in}'}
            
            # Get quote first
            amount_out = self.get_quote(token_in, token_out, amount_in)
            if amount_out == 0:
                raise Exception("Could not get valid quote")
            logger.info(f"Got quote: {amount_out}")

            # Calculate minimum amount out with slippage
            min_amount_out = int(amount_out * (1 - self.slippage))
            logger.info(f"Min amount out with {self.slippage*100}% slippage: {min_amount_out}")

            # Find the best route
            routes = []
            
            # Try direct path first
            direct_path = [token_in, token_out]
            logger.info(f"Trying direct path: {direct_path}")
            direct_route = self._get_route(direct_path, amount_in)
            if direct_route:
                routes = direct_route
                logger.info("Using direct route")
            else:
                raise Exception("No valid route found")

            logger.info(f"Final route: {routes}")

            # Build swap transaction
            deadline = self.w3.eth.get_block('latest')['timestamp'] + 1200  # 20 minutes
            logger.info(f"Transaction deadline: {deadline}")
            
            # Encode the swap function call using functions
            logger.info(f"Swapping with params: amount_in={amount_in}, min_amount_out={min_amount_out}, routes={routes}, address={self.address}, deadline={deadline}")
            swap_function = self.router.functions.swapExactTokensForTokens(
                amount_in,
                min_amount_out,
                routes,
                self.address,
                deadline
            )

            # Build transaction parameters
            # Use fixed gas values like in Uniswap
            tx = self._build_tx(swap_function)
            
            # Get latest nonce right before signing
            tx['nonce'] = self.get_nonce()
            logger.info(f"Built transaction parameters: {tx}")

            # Sign transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.account.key)
            logger.info("Transaction signed")

            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            logger.info(f"Transaction sent: {tx_hash.hex()}")
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)  # Wait up to 5 minutes
            logger.info(f"Transaction receipt: {receipt}")

            if receipt['status'] == 1:
                # Store this as a completed transaction
                token_pair = tuple(sorted([token_in.lower(), token_out.lower()]))
                self._pending_txs[token_pair] = tx_hash.hex()
                return {
                    'success': True,
                    'transactionHash': tx_hash.hex(),
                    'amount_out': min_amount_out,
                    'gas_used': receipt['gasUsed'],
                    'blockNumber': receipt['blockNumber']
                }
            else:
                revert_reason = self._get_revert_reason(receipt)
                return {
                    'success': False,
                    'error': f'Transaction failed: {revert_reason}',
                    'receipt': receipt
                }

        except Exception as e:
            return self._handle_error(e, "executing swap")

    def _get_route(self, path: List[str], amount_in: int) -> List[Tuple[ChecksumAddress, ChecksumAddress, bool, ChecksumAddress]]:
        """Get the best route for a path"""
        try:
            routes = []
            for i in range(len(path) - 1):
                token_in = path[i]
                token_out = path[i + 1]

                # Try both stable and volatile pools
                stable_pool_exists = self.get_pool_exists(token_in, token_out, True)
                volatile_pool_exists = self.get_pool_exists(token_in, token_out, False)

                # Get quotes from both pool types
                stable_quote = 0
                volatile_quote = 0

                if stable_pool_exists:
                    try:
                        stable_route = [Route(token_in, token_out, True, self.factory_address).to_tuple()]
                        stable_quote = self.router.functions.getAmountsOut(amount_in, stable_route).call()[-1]
                        logger.info(f"Stable pool quote: {stable_quote}")
                    except Exception as e:
                        logger.warning(f"Failed to get stable pool quote: {e}")

                if volatile_pool_exists:
                    try:
                        volatile_route = [Route(token_in, token_out, False, self.factory_address).to_tuple()]
                        volatile_quote = self.router.functions.getAmountsOut(amount_in, volatile_route).call()[-1]
                        logger.info(f"Volatile pool quote: {volatile_quote}")
                    except Exception as e:
                        logger.warning(f"Failed to get volatile pool quote: {e}")

                if stable_quote > volatile_quote:
                    routes.append(Route(token_in, token_out, True, self.factory_address))
                    logger.info("Using stable pool - better rate")
                elif volatile_quote > 0:
                    routes.append(Route(token_in, token_out, False, self.factory_address))
                    logger.info("Using volatile pool - better rate")
                else:
                    return []

            return [r.to_tuple() for r in routes]

        except Exception as e:
            error_result = self._handle_error(e, "getting route")
            return []