#!/bin/bash
set -e

# === CONFIGURAÇÕES ===
GUNICORN_WORKERS=3
GUNICORN_PORT=9000
BASE_URL="http://localhost:${GUNICORN_PORT}"
WARMUP_REQUESTS=20

# === CORES PARA OUTPUT ===
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# === FUNÇÕES AUXILIARES ===
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# === SETUP ===
cd /app
source /app/.venv/bin/activate

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "Instalando dependências..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Instalar com UV (silencioso)
uv pip install gunicorn psutil > /dev/null 2>&1

# Verificar instalação
if python -c "import gunicorn" 2>/dev/null; then
    log_success "Gunicorn instalado"
else
    pip install --no-cache-dir gunicorn psutil > /dev/null 2>&1
fi

# Ferramentas do sistema (silencioso)
apt-get update -qq > /dev/null 2>&1
apt-get install -yqq procps curl apache2-utils bc parallel > /dev/null 2>&1

# === ENDPOINTS DISPONÍVEIS ===
echo ""
log_info "Endpoints a testar:"
echo "  1. GET /api/core/issues"
echo "  2. GET /api/core/projects/overview"
echo "  3. GET /api/core/projects/1/desenvolvedores"
echo ""

# === RODAR GUNICORN ===
log_info "Iniciando Gunicorn com ${GUNICORN_WORKERS} workers..."

python -m gunicorn \
    --workers ${GUNICORN_WORKERS} \
    --bind 0.0.0.0:${GUNICORN_PORT} \
    --timeout 120 \
    --worker-class sync \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile /tmp/gunicorn-access.log \
    --error-logfile /tmp/gunicorn-error.log \
    jiboia.jiboia.wsgi:application > /dev/null 2>&1 &

GUNICORN_PID=$!
sleep 8

# Testar endpoint
if curl -s -m 5 ${BASE_URL}/api/core/issues > /dev/null 2>&1; then
    log_success "Gunicorn rodando (PID: $GUNICORN_PID)"
else
    log_error "Erro ao iniciar. Log:"
    cat /tmp/gunicorn-error.log
    exit 1
fi

# === SCRIPT DE MEDIÇÃO DE RAM MELHORADO ===
cat > medir_memoria_completa.py << 'EOF'
import psutil
import sys

def get_process_memory(pid):
    """Calcula memória total do processo e seus filhos"""
    try:
        processo = psutil.Process(pid)
        ram_total = processo.memory_info().rss

        for filho in processo.children(recursive=True):
            try:
                ram_total += filho.memory_info().rss
            except psutil.NoSuchProcess:
                pass

        return ram_total / (1024 * 1024)  # MB
    except Exception as e:
        return 0

def get_system_memory():
    """Memória do sistema completo"""
    mem = psutil.virtual_memory()
    return {
        'total': mem.total / (1024 * 1024),
        'used': mem.used / (1024 * 1024),
        'available': mem.available / (1024 * 1024),
        'percent': mem.percent
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pid = int(sys.argv[1])
        app_mem = get_process_memory(pid)
        print(f"APP_MEM:{app_mem:.2f}")

    sys_mem = get_system_memory()
    print(f"SYS_TOTAL:{sys_mem['total']:.2f}")
    print(f"SYS_USED:{sys_mem['used']:.2f}")
    print(f"SYS_AVAILABLE:{sys_mem['available']:.2f}")
    print(f"SYS_PERCENT:{sys_mem['percent']:.1f}")
EOF

# === FUNÇÃO PARA REQUISIÇÕES PARALELAS ===
make_parallel_requests() {
    local url=$1
    local total=$2
    local concurrent=$3
    local output_file=$4

    # Criar arquivo temporário com URLs
    local url_file=$(mktemp)
    for i in $(seq 1 $total); do
        echo "$url" >> $url_file
    done

    # Executar requisições em paralelo e capturar tempos
    cat $url_file | parallel -j $concurrent --bar \
        "curl -o /dev/null -s -w '%{time_total}\n' {}" 2>/dev/null > $output_file

    rm $url_file
}

# === TESTES DE PERFORMANCE ===
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "           📊 TESTES DE PERFORMANCE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. TESTE DE CRON JOB
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  CRON JOB - Sincronização Jira"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "Sincronizando projeto SM2 do Jira..."

START_TIME=$(date +%s.%N)
python manage.py shell << 'PYTHON_EOF' > /tmp/cron_test.log 2>&1
from jiboia.core.service.jira_svc import JiraService
import time
import psutil
import os

process = psutil.Process(os.getpid())
ram_before = process.memory_info().rss / (1024 * 1024)

start = time.time()
try:
    result = JiraService.sync_all(project_key="SM2")
    success = True
except Exception as e:
    print(f"ERROR: {e}")
    success = False
    result = {}
duration = time.time() - start

ram_after = process.memory_info().rss / (1024 * 1024)
ram_delta = ram_after - ram_before

print(f"RESULT:{success}")
print(f"DURATION:{duration:.2f}")
print(f"RAM_DELTA:{ram_delta:.2f}")
print(f"SYNCED_TYPES:{result.get('issue_types', 0)}")
print(f"SYNCED_STATUS:{result.get('status_types', 0)}")
print(f"SYNCED_ISSUES:{result.get('issues', 0)}")
PYTHON_EOF

END_TIME=$(date +%s.%N)

CRON_RESULT=$(grep "RESULT:" /tmp/cron_test.log | tail -1 | cut -d':' -f2)
CRON_TIME=$(grep "DURATION:" /tmp/cron_test.log | tail -1 | cut -d':' -f2)
CRON_RAM=$(grep "RAM_DELTA:" /tmp/cron_test.log | tail -1 | cut -d':' -f2)
SYNCED_TYPES=$(grep "SYNCED_TYPES:" /tmp/cron_test.log | tail -1 | cut -d':' -f2)
SYNCED_STATUS=$(grep "SYNCED_STATUS:" /tmp/cron_test.log | tail -1 | cut -d':' -f2)
SYNCED_ISSUES=$(grep "SYNCED_ISSUES:" /tmp/cron_test.log | tail -1 | cut -d':' -f2)

if [ "$CRON_RESULT" == "True" ]; then
    log_success "Sincronização concluída"
    echo "   ⏱️  Tempo: ${CRON_TIME}s"
    echo "   💾 RAM: ${CRON_RAM} MB"
    echo "   📊 Dados: ${SYNCED_TYPES} tipos | ${SYNCED_STATUS} status | ${SYNCED_ISSUES} issues"
else
    log_error "Erro na sincronização (veja: /tmp/cron_test.log)"
fi

sleep 3

# 2. WARM-UP (Importante!)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  WARM-UP - Preparando cache"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "Executando ${WARMUP_REQUESTS} requisições de aquecimento..."

for endpoint in "/api/core/issues" "/api/core/projects/overview" "/api/core/projects/1/desenvolvedores"; do
    for i in $(seq 1 $WARMUP_REQUESTS); do
        curl -s ${BASE_URL}${endpoint} > /dev/null 2>&1
    done
done

log_success "Cache aquecido"
sleep 2

# 3. RAM BASELINE
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  MEMÓRIA BASELINE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

RAM_OUTPUT=$(python medir_memoria_completa.py $GUNICORN_PID)
APP_MEM_BASELINE=$(echo "$RAM_OUTPUT" | grep "APP_MEM:" | cut -d':' -f2)
SYS_USED_BASELINE=$(echo "$RAM_OUTPUT" | grep "SYS_USED:" | cut -d':' -f2)
SYS_PERCENT_BASELINE=$(echo "$RAM_OUTPUT" | grep "SYS_PERCENT:" | cut -d':' -f2)

echo "   🔧 App (Gunicorn):     ${APP_MEM_BASELINE} MB"
echo "   💻 Sistema usado:      ${SYS_USED_BASELINE} MB (${SYS_PERCENT_BASELINE}%)"

# 4. LATÊNCIA COM CONCORRÊNCIA CRESCENTE
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  LATÊNCIA SOB CONCORRÊNCIA CRESCENTE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

declare -A LATENCY_RESULTS

for endpoint_name in "issues" "projects" "desenvolvedores"; do
    case $endpoint_name in
        issues) endpoint="/api/core/issues" ;;
        projects) endpoint="/api/core/projects/overview" ;;
        desenvolvedores) endpoint="/api/core/projects/1/desenvolvedores" ;;
    esac

    echo ""
    log_info "Testando: ${endpoint}"

    for concurrency in 1 5 10 20 50; do
        TEMP=$(mktemp)
        make_parallel_requests "${BASE_URL}${endpoint}" 100 $concurrency $TEMP

        # Calcular estatísticas
        TEMP_SORTED=$(mktemp)
        sort -n $TEMP > $TEMP_SORTED

        AVG=$(awk '{s+=$1}END{printf "%.0f", (s/NR)*1000}' $TEMP_SORTED)
        P95=$(sed -n "$((95))p" $TEMP_SORTED | awk '{printf "%.0f", $1*1000}')

        echo "   Concorrência ${concurrency}:  Média=${AVG}ms | P95=${P95}ms"

        # Guardar para relatório final
        LATENCY_RESULTS["${endpoint_name}_c${concurrency}_avg"]=$AVG
        LATENCY_RESULTS["${endpoint_name}_c${concurrency}_p95"]=$P95

        rm $TEMP $TEMP_SORTED
        sleep 1
    done
done

# 5. TESTE DE CARGA MISTA REALISTA
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  CARGA MISTA REALISTA (500 req em 30s)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "Distribuição: 50% issues | 30% projects | 20% devs"
log_info "Concorrência: 20 requisições simultâneas"

# Criar arquivo com mix de URLs
MIXED_URLS=$(mktemp)
for i in $(seq 1 250); do echo "${BASE_URL}/api/core/issues"; done >> $MIXED_URLS
for i in $(seq 1 150); do echo "${BASE_URL}/api/core/projects/overview"; done >> $MIXED_URLS
for i in $(seq 1 100); do echo "${BASE_URL}/api/core/projects/1/desenvolvedores"; done >> $MIXED_URLS

MIXED_OUTPUT=$(mktemp)
START_MIXED=$(date +%s)
cat $MIXED_URLS | parallel -j 20 --bar "curl -o /dev/null -s -w '%{time_total}\n' {}" 2>/dev/null > $MIXED_OUTPUT
END_MIXED=$(date +%s)
DURATION_MIXED=$((END_MIXED - START_MIXED))

# Estatísticas da carga mista
MIXED_SORTED=$(mktemp)
sort -n $MIXED_OUTPUT > $MIXED_SORTED
MIXED_AVG=$(awk '{s+=$1}END{printf "%.0f", (s/NR)*1000}' $MIXED_SORTED)
MIXED_P50=$(sed -n "$((250))p" $MIXED_SORTED | awk '{printf "%.0f", $1*1000}')
MIXED_P95=$(sed -n "$((475))p" $MIXED_SORTED | awk '{printf "%.0f", $1*1000}')
MIXED_P99=$(sed -n "$((495))p" $MIXED_SORTED | awk '{printf "%.0f", $1*1000}')

log_success "Carga concluída em ${DURATION_MIXED}s"
echo "   📊 Média: ${MIXED_AVG}ms | P50: ${MIXED_P50}ms | P95: ${MIXED_P95}ms | P99: ${MIXED_P99}ms"

rm $MIXED_URLS $MIXED_OUTPUT $MIXED_SORTED

# 6. RAM APÓS CARGA
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  MEMÓRIA APÓS CARGA"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

RAM_OUTPUT=$(python medir_memoria_completa.py $GUNICORN_PID)
APP_MEM_CARGA=$(echo "$RAM_OUTPUT" | grep "APP_MEM:" | cut -d':' -f2)
SYS_USED_CARGA=$(echo "$RAM_OUTPUT" | grep "SYS_USED:" | cut -d':' -f2)
SYS_PERCENT_CARGA=$(echo "$RAM_OUTPUT" | grep "SYS_PERCENT:" | cut -d':' -f2)

echo "   🔧 App (Gunicorn):     ${APP_MEM_CARGA} MB"
echo "   💻 Sistema usado:      ${SYS_USED_CARGA} MB (${SYS_PERCENT_CARGA}%)"

# 7. BENCHMARK APACHEBENCH (múltiplas concorrências)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7️⃣  BENCHMARK THROUGHPUT (ApacheBench)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

declare -A AB_RESULTS

for concurrency in 10 50 100; do
    log_info "Testando com concorrência ${concurrency}..."

    ab -n 1000 -c $concurrency -q ${BASE_URL}/api/core/issues > /tmp/ab_c${concurrency}.txt 2>&1

    THROUGHPUT=$(grep "Requests per second" /tmp/ab_c${concurrency}.txt | awk '{print $4}')
    TIME_PER_REQ=$(grep "Time per request" /tmp/ab_c${concurrency}.txt | head -1 | awk '{print $4}')
    FAILED=$(grep "Failed requests" /tmp/ab_c${concurrency}.txt | awk '{print $3}')

    echo "   C=${concurrency}:  ${THROUGHPUT} req/s | ${TIME_PER_REQ}ms/req | ${FAILED} falhas"

    AB_RESULTS["throughput_c${concurrency}"]=$THROUGHPUT
    AB_RESULTS["time_c${concurrency}"]=$TIME_PER_REQ
done

# 8. TAMANHO DAS RESPOSTAS
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8️⃣  TAMANHO DAS RESPOSTAS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

SIZE_ISSUES=$(curl -o /dev/null -s -w '%{size_download}' ${BASE_URL}/api/core/issues 2>/dev/null)
SIZE_PROJECTS=$(curl -o /dev/null -s -w '%{size_download}' ${BASE_URL}/api/core/projects/overview 2>/dev/null)
SIZE_DEVS=$(curl -o /dev/null -s -w '%{size_download}' ${BASE_URL}/api/core/projects/1/desenvolvedores 2>/dev/null)

SIZE_ISSUES_KB=$(echo "scale=1; $SIZE_ISSUES/1024" | bc)
SIZE_PROJECTS_KB=$(echo "scale=1; $SIZE_PROJECTS/1024" | bc)
SIZE_DEVS_KB=$(echo "scale=1; $SIZE_DEVS/1024" | bc)

echo "   /api/core/issues:                  ${SIZE_ISSUES_KB} KB"
echo "   /api/core/projects/overview:       ${SIZE_PROJECTS_KB} KB"
echo "   /api/core/projects/1/desenv:       ${SIZE_DEVS_KB} KB"

# Cálculo de data transfer
AVG_SIZE=$(echo "scale=2; (0.5 * $SIZE_ISSUES + 0.3 * $SIZE_PROJECTS + 0.2 * $SIZE_DEVS)" | bc)
AVG_SIZE_KB=$(echo "scale=1; $AVG_SIZE/1024" | bc)
TOTAL_GB=$(echo "scale=2; 1200000 * $AVG_SIZE / 1024 / 1024 / 1024" | bc)
TOTAL_GB_MARGIN=$(echo "scale=1; $TOTAL_GB * 1.2" | bc)

echo ""
echo "   📦 Tamanho médio ponderado:  ${AVG_SIZE_KB} KB/req"
echo "   📊 Total mensal (1.2M req):  ${TOTAL_GB} GB"
echo "   🔒 Com margem +20%:          ${TOTAL_GB_MARGIN} GB"

# === RELATÓRIO FINAL ===
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        📊 RELATÓRIO FINAL - PERFORMANCE JIBOIA API            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📅 Data: $(date '+%d/%m/%Y %H:%M:%S')"
echo "🏗️  Setup: Gunicorn ${GUNICORN_WORKERS} workers + PostgreSQL 15"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  MÉTRICAS PRINCIPAIS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  💾 MEMÓRIA"
echo "     Baseline: ${APP_MEM_BASELINE} MB | Sob carga: ${APP_MEM_CARGA} MB"
echo "     Sistema: ${SYS_USED_BASELINE} MB → ${SYS_USED_CARGA} MB"
echo ""
echo "  ⚡ LATÊNCIA (Carga Mista - 500 req)"
echo "     Média: ${MIXED_AVG}ms | P50: ${MIXED_P50}ms"
echo "     P95: ${MIXED_P95}ms | P99: ${MIXED_P99}ms"
echo ""
echo "  🔥 THROUGHPUT MÁXIMO"
echo "     C=10:  ${AB_RESULTS[throughput_c10]} req/s"
echo "     C=50:  ${AB_RESULTS[throughput_c50]} req/s"
echo "     C=100: ${AB_RESULTS[throughput_c100]} req/s"
echo ""
echo "  📦 DATA TRANSFER"
echo "     Estimativa mensal: ${TOTAL_GB_MARGIN} GB"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ RECOMENDAÇÕES AWS LIGHTSAIL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Baseado nos resultados:"
echo ""
echo "  • RAM necessária: ~$(echo "$APP_MEM_CARGA * 1.5" | bc | cut -d. -f1) MB (com buffer)"
echo "  • Throughput medido: ${AB_RESULTS[throughput_c50]} req/s"
echo "  • Capacidade mensal: $(echo "${AB_RESULTS[throughput_c50]} * 86400 * 30" | bc) req"
echo "  • Transfer: ${TOTAL_GB_MARGIN} GB/mês"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Cleanup
log_info "Encerrando Gunicorn..."
kill $GUNICORN_PID 2>/dev/null || true

log_success "Testes concluídos!"
echo ""
echo "📁 Logs salvos em:"
echo "   • /tmp/cron_test.log"
echo "   • /tmp/gunicorn-access.log"
echo "   • /tmp/gunicorn-error.log"
echo "   • /tmp/ab_c*.txt"
