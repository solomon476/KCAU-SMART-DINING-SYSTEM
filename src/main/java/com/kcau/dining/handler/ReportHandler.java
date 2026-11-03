package com.kcau.dining.handler;

import com.kcau.dining.service.ReportService;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;

import java.io.IOException;
import java.util.List;
import java.util.Map;

/**
 * Handles HTTP requests for Sales, Order Analytics, and Inventory Reports.
 */
public class ReportHandler implements HttpHandler {

    private final ReportService reportService = new ReportService();

    @Override
    public void handle(HttpExchange exchange) throws IOException {
        if (HttpHelper.handleCorsPreflight(exchange)) return;

        String path = exchange.getRequestURI().getPath();
        String method = exchange.getRequestMethod();

        try {
            if ("/api/reports/summary".equals(path) && "GET".equalsIgnoreCase(method)) {
                Map<String, Object> summary = reportService.getSalesSummary();
                HttpHelper.sendJson(exchange, 200, summary);
            } else if ("/api/reports/sales".equals(path) && "GET".equalsIgnoreCase(method)) {
                List<Map<String, Object>> popularity = reportService.getItemPopularity();
                HttpHelper.sendJson(exchange, 200, popularity);
            } else {
                HttpHelper.sendError(exchange, 404, "Endpoint not found");
            }
        } catch (Exception e) {
            HttpHelper.sendError(exchange, 500, "Server error: " + e.getMessage());
        }
    }
}
