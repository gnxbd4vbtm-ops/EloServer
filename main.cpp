#include <iostream>
#include <string>
#include <vector>
#include <random>
#include <fstream>
#include <thread>
#include <mutex>
#include <curl/curl.h>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

std::mutex printMutex;

std::string getEnvVar(const std::string& key, const std::string& fallback = "") {
    const char* val = std::getenv(key.c_str());
    if (val) return std::string(val);

    std::ifstream env(".env");
    std::string line;
    while (std::getline(env, line)) {
        auto eq = line.find('=');
        if (eq == std::string::npos) continue;
        std::string k = line.substr(0, eq);
        std::string v = line.substr(eq + 1);
        if (k == key) return v;
    }
    return fallback;
}

size_t writeCallback(char* ptr, size_t size, size_t nmemb, std::string* data) {
    data->append(ptr, size * nmemb);
    return size * nmemb;
}

std::string randomName(int length = 8) {
    static const std::string chars =
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    thread_local std::mt19937 rng(std::random_device{}());
    std::uniform_int_distribution<> dist(0, chars.size() - 1);

    std::string result;
    result.reserve(length);
    for (int i = 0; i < length; i++)
        result += chars[dist(rng)];
    return result;
}

struct Player {
    std::string ign, gamemode, cat;
    int elo;
};

Player randomPlayer() {
    static const std::vector<std::string> gamemodes = {
        "mace", "vanilla", "nethPot", "uhc", "diaPot", "sword", "axe", "sword"
    };
    thread_local std::mt19937 rng(std::random_device{}());
    std::uniform_int_distribution<> modeDist(0, gamemodes.size() - 1);
    std::uniform_int_distribution<> eloDist(0, 5000);

    return {randomName(), gamemodes[modeDist(rng)], "no", eloDist(rng)};
}

void workerThread(const std::string& url, const std::string& apiKey,
                  int start, int end, int total) {
    for (int i = start; i <= end; i++) {
        Player p = randomPlayer();

        CURL* curl = curl_easy_init();
        if (!curl) continue;

        json body = {
            {"ign", p.ign},
            {"gamemode", p.gamemode},
            {"elo", p.elo},
            {"cat", p.cat}
        };
        std::string bodyStr = body.dump();
        std::string response;

        struct curl_slist* headers = nullptr;
        headers = curl_slist_append(headers, ("X-API-KEY: " + apiKey).c_str());
        headers = curl_slist_append(headers, "Content-Type: application/json");

        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, bodyStr.c_str());
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, writeCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

        CURLcode res = curl_easy_perform(curl);
        long httpCode = 0;
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &httpCode);

        curl_slist_free_all(headers);
        curl_easy_cleanup(curl);

        std::lock_guard<std::mutex> lock(printMutex);
        if (res != CURLE_OK) {
            std::cerr << "Error on player " << i << ": " << curl_easy_strerror(res) << "\n";
        } else if (httpCode == 200) {
            std::cout << "Created " << i << "/" << total
                      << ": " << p.ign << " | " << p.gamemode
                      << " | " << p.elo << " ELO\n";
        } else {
            std::cerr << "Failed player " << i << ": " << response << "\n";
        }
    }
}

int main() {
    std::string apiKey = getEnvVar("API_KEY");
    if (apiKey.empty()) {
        std::cerr << "API_KEY not found in .env\n";
        return 1;
    }

    std::string baseUrl = getEnvVar("BASE_URL", "http://localhost:8000");
    std::string endpoint = baseUrl + "/api/v1/elo/set/";

    int n, numThreads;
    std::cout << "How many players? ";
    if (!(std::cin >> n)) { std::cerr << "Invalid number\n"; return 1; }
    std::cout << "How many threads? (recommend 16-50): ";
    if (!(std::cin >> numThreads)) { std::cerr << "Invalid number\n"; return 1; }

    curl_global_init(CURL_GLOBAL_DEFAULT);

    std::vector<std::thread> threads;
    int chunkSize = n / numThreads;
    int remainder = n % numThreads;

    int start = 1;
    for (int t = 0; t < numThreads; t++) {
        int end = start + chunkSize - 1;
        if (t == numThreads - 1) end += remainder; // last thread picks up the rest
        threads.emplace_back(workerThread, endpoint, apiKey, start, end, n);
        start = end + 1;
    }

    for (auto& t : threads) t.join();

    curl_global_cleanup();
    return 0;
}
