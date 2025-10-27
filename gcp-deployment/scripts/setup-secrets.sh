#!/bin/bash
# Verolux Enterprise - GCP Secret Manager Setup
# Securely store all sensitive credentials

set -e

PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}

echo "🔐 Setting up GCP Secret Manager..."
echo ""

# Function to create or update secret
create_secret() {
    local secret_name=$1
    local secret_value=$2
    
    echo "Creating secret: ${secret_name}..."
    
    # Delete if exists
    gcloud secrets delete ${secret_name} --quiet 2>/dev/null || true
    
    # Create new secret
    echo -n "${secret_value}" | gcloud secrets create ${secret_name} \
        --data-file=- \
        --replication-policy="automatic" \
        --project=${PROJECT_ID}
}

# 1. Database Password
echo "📊 Setting up database credentials..."
DB_PASSWORD=$(openssl rand -base64 32)
create_secret "verolux-db-password" "${DB_PASSWORD}"

# 2. Database Host
DB_HOST=$(gcloud sql instances describe verolux-db --format='get(connectionName)' 2>/dev/null || echo "verolux-db")
create_secret "verolux-db-host" "${DB_HOST}"

# 3. Firebase Configuration (placeholder - update with your config)
echo "🔥 Setting up Firebase config..."
FIREBASE_CONFIG=$(cat <<EOF
{
  "apiKey": "YOUR_FIREBASE_API_KEY",
  "authDomain": "your-project.firebaseapp.com",
  "projectId": "your-project",
  "storageBucket": "your-project.appspot.com",
  "messagingSenderId": "123456789",
  "appId": "1:123456789:web:abc123"
}
EOF
)
create_secret "verolux-firebase-config" "${FIREBASE_CONFIG}"

# 4. Telegram Bot Token (placeholder - update with your token)
echo "📱 Setting up Telegram bot token..."
create_secret "verolux-telegram-token" "YOUR_TELEGRAM_BOT_TOKEN_HERE"

# 5. Email SMTP Configuration
echo "📧 Setting up email configuration..."
EMAIL_CONFIG=$(cat <<EOF
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_user": "your-email@gmail.com",
  "smtp_password": "your-app-password"
}
EOF
)
create_secret "verolux-email-config" "${EMAIL_CONFIG}"

# 6. WhatsApp API Configuration (placeholder)
echo "💬 Setting up WhatsApp config..."
WHATSAPP_CONFIG=$(cat <<EOF
{
  "api_key": "YOUR_WHATSAPP_API_KEY",
  "phone_number_id": "YOUR_PHONE_NUMBER_ID"
}
EOF
)
create_secret "verolux-whatsapp-config" "${WHATSAPP_CONFIG}"

# 7. Service Account Key
echo "🔑 Creating service account key..."
SA_EMAIL="verolux-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# Delete old key if exists
gcloud iam service-accounts keys list \
    --iam-account=${SA_EMAIL} \
    --filter="keyType=USER_MANAGED" \
    --format="value(name)" | while read key; do
    gcloud iam service-accounts keys delete ${key} --iam-account=${SA_EMAIL} --quiet 2>/dev/null || true
done

# Create new key
gcloud iam service-accounts keys create /tmp/gcp-key.json \
    --iam-account=${SA_EMAIL}

cat /tmp/gcp-key.json | gcloud secrets create verolux-gcp-service-key \
    --data-file=- \
    --replication-policy="automatic" \
    --project=${PROJECT_ID} 2>/dev/null || \
cat /tmp/gcp-key.json | gcloud secrets versions add verolux-gcp-service-key --data-file=-

rm /tmp/gcp-key.json

# 8. Cloud Storage Bucket Name
echo "💾 Setting up storage config..."
BUCKET_NAME="${PROJECT_ID}-verolux-storage"
create_secret "verolux-storage-bucket" "${BUCKET_NAME}"

# 9. API Keys for external services (placeholder)
echo "🔐 Setting up API keys..."
create_secret "verolux-google-maps-api-key" "YOUR_GOOGLE_MAPS_API_KEY"

# Grant access to service account
echo ""
echo "🔒 Granting access to service account..."
SA_EMAIL="verolux-sa@${PROJECT_ID}.iam.gserviceaccount.com"

for secret in verolux-db-password \
              verolux-db-host \
              verolux-firebase-config \
              verolux-telegram-token \
              verolux-email-config \
              verolux-whatsapp-config \
              verolux-gcp-service-key \
              verolux-storage-bucket \
              verolux-google-maps-api-key; do
    
    gcloud secrets add-iam-policy-binding ${secret} \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/secretmanager.secretAccessor" \
        --project=${PROJECT_ID} 2>/dev/null || true
done

echo ""
echo "✅ All secrets configured successfully!"
echo ""
echo "📝 Next Steps:"
echo "1. Update Firebase config: gcloud secrets versions add verolux-firebase-config --data-file=firebase-config.json"
echo "2. Update Telegram token: echo -n 'YOUR_TOKEN' | gcloud secrets versions add verolux-telegram-token --data-file=-"
echo "3. Update email config: gcloud secrets versions add verolux-email-config --data-file=email-config.json"
echo "4. Update WhatsApp config: gcloud secrets versions add verolux-whatsapp-config --data-file=whatsapp-config.json"
echo ""
echo "To view a secret:"
echo "gcloud secrets versions access latest --secret=SECRET_NAME"
echo ""

















