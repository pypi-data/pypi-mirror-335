"""Coinbase AgentKit - Framework for enabling AI agents to take actions onchain."""

from .__version__ import __version__
from .action_providers import (
    Action,
    ActionProvider,
    allora_action_provider,
    basename_action_provider,
    cdp_api_action_provider,
    cdp_wallet_action_provider,
    compound_action_provider,
    create_action,
    erc20_action_provider,
    hyperbolic_action_provider,
    morpho_action_provider,
    pyth_action_provider,
    ssh_action_provider,
    superfluid_action_provider,
    twitter_action_provider,
    wallet_action_provider,
    weth_action_provider,
    wow_action_provider,
)
from .agentkit import AgentKit, AgentKitConfig
from .wallet_providers import (
    CdpWalletProvider,
    CdpWalletProviderConfig,
    EthAccountWalletProvider,
    EthAccountWalletProviderConfig,
    EvmWalletProvider,
    SmartWalletProvider,
    SmartWalletProviderConfig,
    WalletProvider,
)

__all__ = [
    "AgentKit",
    "AgentKitConfig",
    "Action",
    "ActionProvider",
    "create_action",
    "basename_action_provider",
    "WalletProvider",
    "CdpWalletProvider",
    "CdpWalletProviderConfig",
    "EvmWalletProvider",
    "EthAccountWalletProvider",
    "EthAccountWalletProviderConfig",
    "SmartWalletProvider",
    "SmartWalletProviderConfig",
    "allora_action_provider",
    "cdp_api_action_provider",
    "cdp_wallet_action_provider",
    "compound_action_provider",
    "erc20_action_provider",
    "hyperbolic_action_provider",
    "morpho_action_provider",
    "pyth_action_provider",
    "ssh_action_provider",
    "superfluid_action_provider",
    "twitter_action_provider",
    "wallet_action_provider",
    "weth_action_provider",
    "wow_action_provider",
    "__version__",
]
