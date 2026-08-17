---
name: tailscale-setup
description: >-
  Runbook for fixing, configuring, and optimizing Tailscale on Linux, including
  setting up exit nodes, enabling Tailscale SSH, configuring IP forwarding,
  adjusting UFW routing policies, and enabling UDP GRO optimizations.
---

# Tailscale Setup & Exit Node Configuration Runbook

Use this skill when setting up Tailscale, configuring an exit node, enabling Tailscale SSH, or troubleshooting IP forwarding and network performance on Linux.

## 1. System IP Forwarding

Exit nodes and subnet routers require both IPv4 and IPv6 forwarding enabled and persistent.

### A. Sysctl Configuration
Create `/etc/sysctl.d/99-tailscale.conf`:
```bash
sudo bash -c 'cat <<EOF > /etc/sysctl.d/99-tailscale.conf
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
EOF
sysctl -p /etc/sysctl.d/99-tailscale.conf'
```

### B. UFW Sysctl Sync (If UFW is present)
If UFW is installed, ensure `/etc/ufw/sysctl.conf` does not revert forwarding on firewall reloads:
```bash
sudo sed -i 's/#net\/ipv4\/ip_forward=1/net\/ipv4\/ip_forward=1/' /etc/ufw/sysctl.conf
sudo sed -i 's/#net\/ipv6\/conf\/default\/forwarding=1/net\/ipv6\/conf\/default\/forwarding=1/' /etc/ufw/sysctl.conf
sudo sed -i 's/#net\/ipv6\/conf\/all\/forwarding=1/net\/ipv6\/conf\/all\/forwarding=1/' /etc/ufw/sysctl.conf
```

## 2. UFW Routing Configuration

If UFW is active:
1. Allow traffic forwarding in `/etc/default/ufw`:
   ```bash
   sudo sed -i 's/DEFAULT_FORWARD_POLICY="DROP"/DEFAULT_FORWARD_POLICY="ACCEPT"/' /etc/default/ufw
   ```
2. Add interface routing rules:
   ```bash
   sudo ufw route allow in on tailscale0 out on eth0
   sudo ufw route allow in on eth0 out on tailscale0
   sudo ufw reload
   ```

## 3. Network Throughput Optimization (UDP GRO)

Tailscale benefits from UDP GRO forwarding on the primary network interface (e.g. `eth0`):

1. Apply immediately:
   ```bash
   sudo ethtool -K eth0 rx-udp-gro-forwarding on rx-gro-list off
   ```
2. Persist across reboots via `networkd-dispatcher`:
   ```bash
   sudo bash -c 'cat << "EOF" > /etc/networkd-dispatcher/routable.d/50-tailscale
   #!/bin/sh
   ethtool -K eth0 rx-udp-gro-forwarding on rx-gro-list off || true
   EOF
   chmod 755 /etc/networkd-dispatcher/routable.d/50-tailscale'
   ```

## 4. Starting Tailscale Service

Bring up Tailscale with exit node advertisement and SSH support:
```bash
# Note: Use --accept-dns=false if MagicDNS has no public upstream nameservers to avoid resolving issues
sudo tailscale up --advertise-exit-node --ssh --accept-dns=false
```

## 5. Verification & Admin Console Approval

1. **Verify Local Status**:
   ```bash
   sudo tailscale status
   sudo tailscale status --json | jq '{BackendState, Health}'
   ```
2. **Admin Console Approval**:
   - Navigate to [Tailscale Admin Console](https://login.tailscale.com/admin/machines).
   - Locate the node -> **Edit route settings...** -> enable **Use as exit node** (`0.0.0.0/0`, `::/0`).
