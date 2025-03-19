use std::sync::Arc;

use axum::extract::Path;
use axum::http::StatusCode;
use serde::Deserialize;

use axum::{extract::State, Json};
use axum_extra::extract::Query;

use crate::base::spec;
use crate::lib_context::LibContext;
use crate::ops::interface::QueryResponse;

use super::error::ApiError;

#[derive(Debug, Deserialize)]
pub struct SearchParams {
    handler: Option<String>,
    field: Option<String>,
    query: String,
    limit: u32,
    metric: Option<spec::VectorSimilarityMetric>,
}

pub async fn search(
    Path(flow_name): Path<String>,
    Query(query): Query<SearchParams>,
    State(lib_context): State<Arc<LibContext>>,
) -> Result<Json<QueryResponse>, ApiError> {
    let query_handler = lib_context.with_flow_context(&flow_name, |flow_ctx| {
        Ok(match &query.handler {
            Some(handler) => flow_ctx
                .query_handlers
                .get(handler)
                .ok_or_else(|| {
                    ApiError::new(
                        &format!("Query handler not found: {handler}"),
                        StatusCode::NOT_FOUND,
                    )
                })?
                .clone(),
            None => {
                if flow_ctx.query_handlers.len() == 0 {
                    return Err(ApiError::new(
                        &format!("No query handler found for flow: {flow_name}"),
                        StatusCode::NOT_FOUND,
                    ));
                } else if flow_ctx.query_handlers.len() == 1 {
                    flow_ctx.query_handlers.values().next().unwrap().clone()
                } else {
                    return Err(ApiError::new(
                        "Found multiple query handlers for flow {}",
                        StatusCode::BAD_REQUEST,
                    ));
                }
            }
        })
    })??;
    let (results, info) = query_handler
        .search(query.query, query.limit, query.field, query.metric)
        .await?;
    let response = QueryResponse {
        results,
        info: serde_json::to_value(info).map_err(|e| {
            ApiError::new(
                &format!("Failed to serialize query info: {e}"),
                StatusCode::INTERNAL_SERVER_ERROR,
            )
        })?,
    };
    Ok(Json(response))
}
