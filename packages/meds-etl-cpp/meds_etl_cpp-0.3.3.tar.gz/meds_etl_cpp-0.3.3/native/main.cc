#include "perform_etl.hh"

int main() {
    size_t num_shards = 2;

    std::string path_to_folder =
        "/home/ethanid/health_research/mimic-iv-demo-meds9/temp";
    std::string output = "/home/ethanid/health_research/mimic-iv-demo-meds9/ok";

    perform_etl(path_to_folder, output, 100, 6);
}
