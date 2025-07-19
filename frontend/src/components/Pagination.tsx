import React from 'react';
import { PaginationInfo } from '../types';

interface PaginationProps {
  pagination: PaginationInfo;
  onPageChange: (page: number) => void;
  onPageSizeChange: (pageSize: number) => void;
  loading?: boolean;
}

const Pagination: React.FC<PaginationProps> = ({
  pagination,
  onPageChange,
  onPageSizeChange,
  loading = false
}) => {
  const { page, page_size, total, total_pages, has_next, has_prev } = pagination;

  // 计算显示的页码范围
  const getPageRange = () => {
    const range = [];
    const delta = 2; // 当前页前后显示的页数
    let start = Math.max(1, page - delta);
    let end = Math.min(total_pages, page + delta);

    // 调整范围以确保显示足够的页码
    if (end - start < 4) {
      if (start === 1) {
        end = Math.min(total_pages, start + 4);
      } else if (end === total_pages) {
        start = Math.max(1, end - 4);
      }
    }

    for (let i = start; i <= end; i++) {
      range.push(i);
    }
    return range;
  };

  const pageRange = getPageRange();

  const handleJumpToPage = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      const target = event.target as HTMLInputElement;
      const newPage = parseInt(target.value);
      if (newPage && newPage >= 1 && newPage <= total_pages) {
        onPageChange(newPage);
      }
      target.value = '';
    }
  };

  if (total === 0) {
    return null;
  }

  return (
    <div className="flex items-center justify-between px-4 py-3 bg-white border-t border-gray-200 sm:px-6">
      <div className="flex items-center text-sm text-gray-700">
        <span>每页显示</span>
        <select
          value={page_size}
          onChange={(e) => onPageSizeChange(Number(e.target.value))}
          disabled={loading}
          className="mx-2 px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
        >
          <option value={10}>10</option>
          <option value={20}>20</option>
          <option value={50}>50</option>
          <option value={100}>100</option>
        </select>
        <span>条，共 {total} 条记录</span>
      </div>

      <div className="flex items-center space-x-2">
        {/* 跳转到指定页 */}
        <div className="flex items-center space-x-2 mr-4">
          <span className="text-sm text-gray-700">跳转到</span>
          <input
            type="number"
            min="1"
            max={total_pages}
            placeholder={page.toString()}
            onKeyPress={handleJumpToPage}
            disabled={loading}
            className="w-16 px-2 py-1 border border-gray-300 rounded text-sm text-center focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
          />
          <span className="text-sm text-gray-700">页</span>
        </div>

        {/* 上一页 */}
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={!has_prev || loading}
          className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
        >
          上一页
        </button>

        {/* 页码 */}
        <div className="flex space-x-1">
          {/* 第一页 */}
          {pageRange[0] > 1 && (
            <>
              <button
                onClick={() => onPageChange(1)}
                disabled={loading}
                className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:bg-gray-100"
              >
                1
              </button>
              {pageRange[0] > 2 && (
                <span className="px-2 py-1 text-sm text-gray-500">...</span>
              )}
            </>
          )}

          {/* 页码范围 */}
          {pageRange.map((pageNum) => (
            <button
              key={pageNum}
              onClick={() => onPageChange(pageNum)}
              disabled={loading}
              className={`px-3 py-1 text-sm border rounded disabled:cursor-not-allowed ${
                pageNum === page
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'border-gray-300 hover:bg-gray-50 disabled:bg-gray-100'
              }`}
            >
              {pageNum}
            </button>
          ))}

          {/* 最后一页 */}
          {pageRange[pageRange.length - 1] < total_pages && (
            <>
              {pageRange[pageRange.length - 1] < total_pages - 1 && (
                <span className="px-2 py-1 text-sm text-gray-500">...</span>
              )}
              <button
                onClick={() => onPageChange(total_pages)}
                disabled={loading}
                className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:bg-gray-100"
              >
                {total_pages}
              </button>
            </>
          )}
        </div>

        {/* 下一页 */}
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={!has_next || loading}
          className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
        >
          下一页
        </button>
      </div>

      <div className="text-sm text-gray-700">
        第 {page} 页，共 {total_pages} 页
      </div>
    </div>
  );
};

export default Pagination; 