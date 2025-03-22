#include "compas.h"

// Forward declarations
void init_booleans(nb::module_ &);

/**
 * @brief Module initialization function for COMPAS CGAL extension
 * 
 * @param m Nanobind module instance
 * @details Initializes the Python module by defining functions and their bindings.
 *          Each function is exposed to Python with appropriate documentation.
 */
NB_MODULE(test_my_binding_ext, m) {
    m.doc() = "CGAL via Nanobind says hello to COMPAS!";
        
    init_booleans(m);

}
