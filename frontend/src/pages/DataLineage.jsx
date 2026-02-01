import { useState, useEffect, useCallback, useRef } from "react";
import { Card, Typography, Tag, Spin, Empty, Tooltip, message } from "antd";

const { Title, Text } = Typography;

const TYPE_CONFIG = {
  ods: { color: "#1677ff", label: "ODS", column: 0 },
  dw: { color: "#52c41a", label: "DW", column: 1 },
  dm: { color: "#fa8c16", label: "DM", column: 2 },
};

const STATUS_COLOR = {
  active: "#52c41a",
  degraded: "#fa8c16",
  paused: "#d9d9d9",
};

export default function DataLineage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [edgePositions, setEdgePositions] = useState([]);
  const [hoveredEdge, setHoveredEdge] = useState(null);
  const containerRef = useRef(null);
  const nodeRefs = useRef({});

  useEffect(() => {
    setLoading(true);
    fetch("/api/lineage")
      .then((r) => r.json())
      .then(setData)
      .catch(() => message.error("加载血缘数据失败"))
      .finally(() => setLoading(false));
  }, []);

  const calcEdgePositions = useCallback(() => {
    if (!data || !containerRef.current) return;
    const containerRect = containerRef.current.getBoundingClientRect();
    const positions = data.edges
      .map((edge) => {
        const srcEl = nodeRefs.current[edge.source];
        const tgtEl = nodeRefs.current[edge.target];
        if (!srcEl || !tgtEl) return null;
        const srcRect = srcEl.getBoundingClientRect();
        const tgtRect = tgtEl.getBoundingClientRect();
        return {
          ...edge,
          x1: srcRect.right - containerRect.left,
          y1: srcRect.top + srcRect.height / 2 - containerRect.top,
          x2: tgtRect.left - containerRect.left,
          y2: tgtRect.top + tgtRect.height / 2 - containerRect.top,
        };
      })
      .filter(Boolean);
    setEdgePositions(positions);
  }, [data]);

  useEffect(() => {
    if (!data) return;
    // Wait for DOM to render nodes before calculating positions
    const timer = setTimeout(calcEdgePositions, 100);
    window.addEventListener("resize", calcEdgePositions);
    return () => {
      clearTimeout(timer);
      window.removeEventListener("resize", calcEdgePositions);
    };
  }, [data, calcEdgePositions]);

  if (loading) {
    return (
      <div style={{ textAlign: "center", paddingTop: 120 }}>
        <Spin size="large" tip="加载血缘数据..." />
      </div>
    );
  }

  if (!data || data.nodes.length === 0) {
    return (
      <div>
        <Title level={4} style={{ marginBottom: 24 }}>
          数据血缘
        </Title>
        <Empty description="暂无血缘数据" />
      </div>
    );
  }

  // Group nodes by type
  const columns = { ods: [], dw: [], dm: [] };
  data.nodes.forEach((node) => {
    if (columns[node.type]) columns[node.type].push(node);
  });

  const columnHeaders = [
    { type: "ods", label: "ODS 源数据层" },
    { type: "dw", label: "DW 数仓层" },
    { type: "dm", label: "DM 数据集市层" },
  ];

  return (
    <div>
      <Title level={4} style={{ marginBottom: 24 }}>
        数据血缘
      </Title>

      <Card size="small">
        <div
          ref={containerRef}
          style={{
            position: "relative",
            display: "flex",
            gap: 48,
            minHeight: 400,
            padding: "16px 0",
          }}
        >
          {/* SVG overlay for edges */}
          <svg
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: "100%",
              pointerEvents: "none",
              overflow: "visible",
            }}
          >
            <defs>
              {Object.entries(STATUS_COLOR).map(([key, fill]) => (
                <marker
                  key={key}
                  id={`arrowhead-${key}`}
                  markerWidth="8"
                  markerHeight="6"
                  refX="8"
                  refY="3"
                  orient="auto"
                >
                  <polygon points="0 0, 8 3, 0 6" fill={fill} />
                </marker>
              ))}
            </defs>
            {edgePositions.map((edge, idx) => {
              const midX = (edge.x1 + edge.x2) / 2;
              const color = STATUS_COLOR[edge.status] || STATUS_COLOR.active;
              const isHovered = hoveredEdge === idx;
              return (
                <g key={idx}>
                  {/* Invisible wider path for hover detection */}
                  <path
                    d={`M ${edge.x1} ${edge.y1} C ${midX} ${edge.y1}, ${midX} ${edge.y2}, ${edge.x2} ${edge.y2}`}
                    fill="none"
                    stroke="transparent"
                    strokeWidth={12}
                    style={{ pointerEvents: "stroke", cursor: "pointer" }}
                    onMouseEnter={() => setHoveredEdge(idx)}
                    onMouseLeave={() => setHoveredEdge(null)}
                  />
                  <path
                    d={`M ${edge.x1} ${edge.y1} C ${midX} ${edge.y1}, ${midX} ${edge.y2}, ${edge.x2} ${edge.y2}`}
                    fill="none"
                    stroke={color}
                    strokeWidth={isHovered ? 3 : 1.5}
                    strokeDasharray={edge.status === "paused" ? "6 4" : "none"}
                    markerEnd={`url(#arrowhead-${edge.status || "active"})`}
                    style={{ transition: "stroke-width 0.2s" }}
                  />
                </g>
              );
            })}
          </svg>

          {/* Tooltip for hovered edge */}
          {hoveredEdge !== null && edgePositions[hoveredEdge] && (
            <div
              style={{
                position: "absolute",
                left:
                  (edgePositions[hoveredEdge].x1 +
                    edgePositions[hoveredEdge].x2) /
                    2 -
                  60,
                top:
                  (edgePositions[hoveredEdge].y1 +
                    edgePositions[hoveredEdge].y2) /
                    2 -
                  36,
                background: "rgba(0,0,0,0.75)",
                color: "#fff",
                padding: "4px 12px",
                borderRadius: 4,
                fontSize: 12,
                whiteSpace: "nowrap",
                pointerEvents: "none",
                zIndex: 10,
              }}
            >
              管道: {edgePositions[hoveredEdge].pipeline}
              <br />
              状态: {edgePositions[hoveredEdge].status}
            </div>
          )}

          {/* Three columns */}
          {columnHeaders.map(({ type, label }) => (
            <div
              key={type}
              style={{
                flex: 1,
                display: "flex",
                flexDirection: "column",
                gap: 12,
              }}
            >
              <div style={{ textAlign: "center", marginBottom: 8 }}>
                <Tag color={TYPE_CONFIG[type].color}>{label}</Tag>
              </div>
              {columns[type].map((node) => (
                <div
                  key={node.id}
                  ref={(el) => {
                    nodeRefs.current[node.id] = el;
                  }}
                  style={{
                    padding: "10px 14px",
                    borderRadius: 6,
                    border: `1.5px solid ${TYPE_CONFIG[type].color}`,
                    background: `${TYPE_CONFIG[type].color}10`,
                    cursor: "default",
                  }}
                >
                  <Tooltip title={`${TYPE_CONFIG[type].label} · ${node.id}`}>
                    <Text
                      strong
                      style={{ color: TYPE_CONFIG[type].color, fontSize: 13 }}
                    >
                      {node.id}
                    </Text>
                  </Tooltip>
                </div>
              ))}
              {columns[type].length === 0 && (
                <Text
                  type="secondary"
                  style={{ textAlign: "center", marginTop: 40 }}
                >
                  暂无表
                </Text>
              )}
            </div>
          ))}
        </div>

        {/* Legend */}
        <div
          style={{
            marginTop: 16,
            display: "flex",
            gap: 24,
            justifyContent: "center",
          }}
        >
          {[
            { label: "Active", color: STATUS_COLOR.active },
            { label: "Degraded", color: STATUS_COLOR.degraded },
            { label: "Paused", color: STATUS_COLOR.paused, dashed: true },
          ].map(({ label, color, dashed }) => (
            <Text key={label} type="secondary" style={{ fontSize: 12 }}>
              <span
                style={{
                  display: "inline-block",
                  width: 24,
                  height: 2,
                  background: color,
                  verticalAlign: "middle",
                  marginRight: 4,
                  ...(dashed
                    ? { borderTop: "2px dashed #d9d9d9", background: "none" }
                    : {}),
                }}
              />
              {label}
            </Text>
          ))}
        </div>
      </Card>
    </div>
  );
}
