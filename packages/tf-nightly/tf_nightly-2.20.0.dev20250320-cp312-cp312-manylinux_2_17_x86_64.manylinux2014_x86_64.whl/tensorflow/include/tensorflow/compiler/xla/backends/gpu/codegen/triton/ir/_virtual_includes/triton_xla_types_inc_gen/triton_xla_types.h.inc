/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* TypeDef Declarations                                                       *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

#ifdef GET_TYPEDEF_CLASSES
#undef GET_TYPEDEF_CLASSES


namespace mlir {
class AsmParser;
class AsmPrinter;
} // namespace mlir
namespace mlir {
namespace triton {
namespace xla {
class TiledTensorType;
namespace detail {
struct TiledTensorTypeStorage;
} // namespace detail
class TiledTensorType : public ::mlir::Type::TypeBase<TiledTensorType, ::mlir::Type, detail::TiledTensorTypeStorage, ::mlir::ValueSemantics> {
public:
  using Base::Base;
  RankedTensorType getOriginalType() const {
    return RankedTensorType::get(getOriginalShape(), getElementType());
  }
  RankedTensorType getTileType() const {
    return RankedTensorType::get(getTileShape(), getElementType());
  }
  int64_t getRank() const {
    return getOriginalShape().size();
  }
  static constexpr ::llvm::StringLiteral name = "triton_xla.tiled_tensor";
  static constexpr ::llvm::StringLiteral dialectName = "triton_xla";
  using Base::getChecked;
  static TiledTensorType get(::mlir::MLIRContext *context, ::llvm::ArrayRef<int64_t> tile_shape, ::llvm::ArrayRef<int64_t> original_shape, Type element_type);
  static TiledTensorType getChecked(::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError, ::mlir::MLIRContext *context, ::llvm::ArrayRef<int64_t> tile_shape, ::llvm::ArrayRef<int64_t> original_shape, Type element_type);
  static TiledTensorType get(::mlir::MLIRContext *context, RankedTensorType tile_type, RankedTensorType original_type);
  static TiledTensorType getChecked(::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError, ::mlir::MLIRContext *context, RankedTensorType tile_type, RankedTensorType original_type);
  static ::llvm::LogicalResult verify(::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError, ::llvm::ArrayRef<int64_t> tile_shape, ::llvm::ArrayRef<int64_t> original_shape, Type element_type);
  static ::llvm::LogicalResult verifyInvariants(::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError, ::llvm::ArrayRef<int64_t> tile_shape, ::llvm::ArrayRef<int64_t> original_shape, Type element_type);
  static constexpr ::llvm::StringLiteral getMnemonic() {
    return {"tiled_tensor"};
  }

  static ::mlir::Type parse(::mlir::AsmParser &odsParser);
  void print(::mlir::AsmPrinter &odsPrinter) const;
  ::llvm::ArrayRef<int64_t> getTileShape() const;
  ::llvm::ArrayRef<int64_t> getOriginalShape() const;
  Type getElementType() const;
};
} // namespace xla
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::xla::TiledTensorType)

#endif  // GET_TYPEDEF_CLASSES

