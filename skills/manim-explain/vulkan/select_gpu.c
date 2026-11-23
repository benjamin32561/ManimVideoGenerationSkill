/*
 * VK_LAYER_EXPLAIN_select_gpu: an explicit Vulkan layer that shows the application only the
 * physical device on one PCI bus.
 *
 * Why: on a machine with several identical NVIDIA GPUs, NVIDIA's Vulkan driver ignores
 * CUDA_VISIBLE_DEVICES, and wgpu's WGPU_ADAPTER_NAME matches on the device name, which is
 * the same for every card, so wgpu (inside manimgx) always takes GPU 0. The system Vulkan
 * loader (1.2.131) predates VK_LOADER_DEVICE_SELECT, and that selects by vendor:device id
 * anyway, again identical. This layer filters vkEnumeratePhysicalDevices and
 * vkEnumeratePhysicalDeviceGroups down to the device whose PCI bus number equals the hex
 * value in EXPLAIN_VK_PCI_BUS (e.g. "3b", from `nvidia-smi -i <index> --query-gpu=pci.bus_id`).
 *
 * Enable: VK_LAYER_PATH=<dir with the manifest> VK_INSTANCE_LAYERS=VK_LAYER_EXPLAIN_select_gpu
 *         EXPLAIN_VK_PCI_BUS=3b
 * If EXPLAIN_VK_PCI_BUS is unset the layer passes everything through. If no device matches it
 * returns zero devices (so the failure is visible: manimgx then reports lavapipe).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <vulkan/vulkan.h>
#include <vulkan/vk_layer.h>

#define EXPORT __attribute__((visibility("default")))

static PFN_vkGetInstanceProcAddr g_next_gipa = NULL; /* the next link's vkGetInstanceProcAddr */
static PFN_vkGetDeviceProcAddr g_next_gdpa = NULL;   /* the next link's vkGetDeviceProcAddr */
/* Next-link entry points, resolved inside vkCreateInstance: afterwards the loader's
 * terminator GIPA resolves through the top-of-chain table and would hand back our own
 * hooks (infinite recursion). They are the same for every instance in the process. */
static PFN_vkEnumeratePhysicalDevices g_next_enum = NULL;
static PFN_vkEnumeratePhysicalDeviceGroups g_next_enum_groups = NULL;
static PFN_vkGetPhysicalDeviceProperties2 g_next_props2 = NULL;

/*
 * wanted_bus: the PCI bus number to keep, parsed from EXPLAIN_VK_PCI_BUS (hex).
 * Returns -1 when the variable is unset or empty (pass-through mode).
 */
static long wanted_bus(void) {
    const char *s = getenv("EXPLAIN_VK_PCI_BUS");
    if (s == NULL || *s == '\0') return -1;
    return strtol(s, NULL, 16);
}

/*
 * device_bus: the PCI bus number of a physical device, via VK_EXT_pci_bus_info chained
 * into vkGetPhysicalDeviceProperties2. Returns -1 if the query is unavailable.
 */
static long device_bus(VkPhysicalDevice pd) {
    PFN_vkGetPhysicalDeviceProperties2 gp2 = g_next_props2;
    if (gp2 == NULL) return -1;
    VkPhysicalDevicePCIBusInfoPropertiesEXT bus;
    memset(&bus, 0, sizeof bus);
    bus.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PCI_BUS_INFO_PROPERTIES_EXT;
    VkPhysicalDeviceProperties2 props;
    memset(&props, 0, sizeof props);
    props.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PROPERTIES_2;
    props.pNext = &bus;
    gp2(pd, &props);
    return (long)bus.pciBus;
}

/*
 * layer_CreateInstance: advance the loader's layer chain, remember the next link's
 * vkGetInstanceProcAddr, create the instance below us, and resolve the next link's
 * enumeration and properties entry points while the loader's table still points down.
 */
static VKAPI_ATTR VkResult VKAPI_CALL layer_CreateInstance(const VkInstanceCreateInfo *info,
                                                        const VkAllocationCallbacks *alloc,
                                                        VkInstance *out) {
    VkLayerInstanceCreateInfo *chain = (VkLayerInstanceCreateInfo *)info->pNext;
    while (chain && !(chain->sType == VK_STRUCTURE_TYPE_LOADER_INSTANCE_CREATE_INFO &&
                      chain->function == VK_LAYER_LINK_INFO))
        chain = (VkLayerInstanceCreateInfo *)chain->pNext;
    if (chain == NULL) return VK_ERROR_INITIALIZATION_FAILED;
    g_next_gipa = chain->u.pLayerInfo->pfnNextGetInstanceProcAddr;
    chain->u.pLayerInfo = chain->u.pLayerInfo->pNext;
    PFN_vkCreateInstance next = (PFN_vkCreateInstance)g_next_gipa(VK_NULL_HANDLE, "vkCreateInstance");
    VkResult r = next(info, alloc, out);
    if (r != VK_SUCCESS) return r;
    VkInstance inst = *out;
    g_next_enum = (PFN_vkEnumeratePhysicalDevices)g_next_gipa(inst, "vkEnumeratePhysicalDevices");
    g_next_enum_groups =
        (PFN_vkEnumeratePhysicalDeviceGroups)g_next_gipa(inst, "vkEnumeratePhysicalDeviceGroups");
    if (g_next_enum_groups == NULL)
        g_next_enum_groups = (PFN_vkEnumeratePhysicalDeviceGroups)g_next_gipa(
            inst, "vkEnumeratePhysicalDeviceGroupsKHR");
    g_next_props2 =
        (PFN_vkGetPhysicalDeviceProperties2)g_next_gipa(inst, "vkGetPhysicalDeviceProperties2");
    if (g_next_props2 == NULL)
        g_next_props2 = (PFN_vkGetPhysicalDeviceProperties2)g_next_gipa(
            inst, "vkGetPhysicalDeviceProperties2KHR");
    return VK_SUCCESS;
}

/*
 * layer_EnumeratePhysicalDevices: the two-call enumeration, keeping only devices on the
 * wanted PCI bus (all devices in pass-through mode).
 */
static VKAPI_ATTR VkResult VKAPI_CALL layer_EnumeratePhysicalDevices(VkInstance instance,
                                                                  uint32_t *count,
                                                                  VkPhysicalDevice *out) {
    PFN_vkEnumeratePhysicalDevices next = g_next_enum;
    long want = wanted_bus();
    if (want < 0) return next(instance, count, out);
    uint32_t n = 0;
    VkResult r = next(instance, &n, NULL);
    if (r != VK_SUCCESS) return r;
    VkPhysicalDevice *all = calloc(n ? n : 1, sizeof *all);
    r = next(instance, &n, all);
    if (r != VK_SUCCESS && r != VK_INCOMPLETE) { free(all); return r; }
    uint32_t kept = 0;
    for (uint32_t i = 0; i < n; i++)
        if (device_bus(all[i]) == want) all[kept++] = all[i];
    if (out == NULL) { *count = kept; free(all); return VK_SUCCESS; }
    uint32_t w = kept < *count ? kept : *count;
    memcpy(out, all, w * sizeof *all);
    *count = w;
    free(all);
    return w < kept ? VK_INCOMPLETE : VK_SUCCESS;
}

/*
 * layer_EnumeratePhysicalDeviceGroups: the same filter for device groups; a group survives
 * when its first device is on the wanted bus. Keeps the caller's sType/pNext.
 */
static VKAPI_ATTR VkResult VKAPI_CALL layer_EnumeratePhysicalDeviceGroups(
    VkInstance instance, uint32_t *count, VkPhysicalDeviceGroupProperties *out) {
    PFN_vkEnumeratePhysicalDeviceGroups next = g_next_enum_groups;
    long want = wanted_bus();
    if (want < 0) return next(instance, count, out);
    uint32_t n = 0;
    VkResult r = next(instance, &n, NULL);
    if (r != VK_SUCCESS) return r;
    VkPhysicalDeviceGroupProperties *all = calloc(n ? n : 1, sizeof *all);
    for (uint32_t i = 0; i < n; i++) all[i].sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_GROUP_PROPERTIES;
    r = next(instance, &n, all);
    if (r != VK_SUCCESS && r != VK_INCOMPLETE) { free(all); return r; }
    uint32_t kept = 0;
    for (uint32_t i = 0; i < n; i++)
        if (all[i].physicalDeviceCount > 0 && device_bus(all[i].physicalDevices[0]) == want)
            all[kept++] = all[i];
    if (out == NULL) { *count = kept; free(all); return VK_SUCCESS; }
    uint32_t w = kept < *count ? kept : *count;
    for (uint32_t i = 0; i < w; i++) {
        out[i].physicalDeviceCount = all[i].physicalDeviceCount;
        memcpy(out[i].physicalDevices, all[i].physicalDevices, sizeof all[i].physicalDevices);
        out[i].subsetAllocation = all[i].subsetAllocation;
    }
    *count = w;
    free(all);
    return w < kept ? VK_INCOMPLETE : VK_SUCCESS;
}

/*
 * layer_CreateDevice: advance the device chain and remember the next vkGetDeviceProcAddr;
 * the layer changes nothing at device level.
 */
static VKAPI_ATTR VkResult VKAPI_CALL layer_CreateDevice(VkPhysicalDevice pd,
                                                      const VkDeviceCreateInfo *info,
                                                      const VkAllocationCallbacks *alloc,
                                                      VkDevice *out) {
    VkLayerDeviceCreateInfo *chain = (VkLayerDeviceCreateInfo *)info->pNext;
    while (chain && !(chain->sType == VK_STRUCTURE_TYPE_LOADER_DEVICE_CREATE_INFO &&
                      chain->function == VK_LAYER_LINK_INFO))
        chain = (VkLayerDeviceCreateInfo *)chain->pNext;
    if (chain == NULL) return VK_ERROR_INITIALIZATION_FAILED;
    PFN_vkGetInstanceProcAddr gipa = chain->u.pLayerInfo->pfnNextGetInstanceProcAddr;
    g_next_gdpa = chain->u.pLayerInfo->pfnNextGetDeviceProcAddr;
    chain->u.pLayerInfo = chain->u.pLayerInfo->pNext;
    PFN_vkCreateDevice next = (PFN_vkCreateDevice)gipa(VK_NULL_HANDLE, "vkCreateDevice");
    return next(pd, info, alloc, out);
}

EXPORT VKAPI_ATTR PFN_vkVoidFunction VKAPI_CALL layer_GetDeviceProcAddr(VkDevice device, const char *name);

/*
 * layer_GetInstanceProcAddr: our entry points by name, everything else from the next link.
 */
EXPORT VKAPI_ATTR PFN_vkVoidFunction VKAPI_CALL layer_GetInstanceProcAddr(VkInstance instance,
                                                                       const char *name) {
    if (!strcmp(name, "vkGetInstanceProcAddr")) return (PFN_vkVoidFunction)layer_GetInstanceProcAddr;
    if (!strcmp(name, "vkGetDeviceProcAddr")) return (PFN_vkVoidFunction)layer_GetDeviceProcAddr;
    if (!strcmp(name, "vkCreateInstance")) return (PFN_vkVoidFunction)layer_CreateInstance;
    if (!strcmp(name, "vkCreateDevice")) return (PFN_vkVoidFunction)layer_CreateDevice;
    if (!strcmp(name, "vkEnumeratePhysicalDevices"))
        return (PFN_vkVoidFunction)layer_EnumeratePhysicalDevices;
    if (!strcmp(name, "vkEnumeratePhysicalDeviceGroups") ||
        !strcmp(name, "vkEnumeratePhysicalDeviceGroupsKHR"))
        return (PFN_vkVoidFunction)layer_EnumeratePhysicalDeviceGroups;
    return g_next_gipa ? g_next_gipa(instance, name) : NULL;
}

/*
 * layer_GetDeviceProcAddr: pass-through to the next link (the layer has no device hooks).
 */
EXPORT VKAPI_ATTR PFN_vkVoidFunction VKAPI_CALL layer_GetDeviceProcAddr(VkDevice device,
                                                                     const char *name) {
    if (!strcmp(name, "vkGetDeviceProcAddr")) return (PFN_vkVoidFunction)layer_GetDeviceProcAddr;
    return g_next_gdpa ? g_next_gdpa(device, name) : NULL;
}

/*
 * vkNegotiateLoaderLayerInterfaceVersion: loader-layer interface v2 handshake.
 */
EXPORT VKAPI_ATTR VkResult VKAPI_CALL vkNegotiateLoaderLayerInterfaceVersion(
    VkNegotiateLayerInterface *v) {
    if (v->loaderLayerInterfaceVersion > 2) v->loaderLayerInterfaceVersion = 2;
    v->pfnGetInstanceProcAddr = layer_GetInstanceProcAddr;
    v->pfnGetDeviceProcAddr = layer_GetDeviceProcAddr;
    v->pfnGetPhysicalDeviceProcAddr = NULL;
    return VK_SUCCESS;
}
