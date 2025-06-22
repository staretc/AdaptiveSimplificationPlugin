def classFactory(iface):
    from .geometricsimplification_plugin import GeometricSimplificationPlugin
    return GeometricSimplificationPlugin(iface)